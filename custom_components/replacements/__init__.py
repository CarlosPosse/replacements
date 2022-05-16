"""The replacements integration."""
import logging

from homeassistant import config_entries
from homeassistant.helpers import discovery
from homeassistant.helpers.entity_component import EntityComponent
from integrationhelper.const import CC_STARTUP_VERSION

from .const import (CONF_SENSORS, DOMAIN, ISSUE_URL, PLATFORM, SERVICE_DATE,
                    SERVICE_DATE_SCHEMA, SERVICE_REPLACED,
                    SERVICE_REPLACED_SCHEMA, SERVICE_STOCK,
                    SERVICE_STOCK_SCHEMA, VERSION)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    """Set up this component using YAML."""
    component = EntityComponent(_LOGGER, DOMAIN, hass)

    # Check if domain is configured
    if DOMAIN not in config:
        return True

    # log startup message
    _LOGGER.info(
        CC_STARTUP_VERSION.format(name=DOMAIN, version=VERSION, issue_link=ISSUE_URL)
    )

    # Get all platforms defined inside the domain
    platform_config = config[DOMAIN].get(CONF_SENSORS, {})
    if not platform_config:
        return False

    # Load every platform in the main loop
    for entry in platform_config:
        hass.async_create_task(
            discovery.async_load_platform(hass, PLATFORM, DOMAIN, entry, config)
        )
    
    # Initialize all entries configured in the UI
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_IMPORT}, data={}
        )
    )

    # Register the stock update service
    component.async_register_entity_service(
        SERVICE_STOCK, SERVICE_STOCK_SCHEMA, "async_handle_renew_stock"
    )
    
    # Register the set date service
    component.async_register_entity_service(
        SERVICE_DATE, SERVICE_DATE_SCHEMA, "async_handle_set_date"
    )
    
    # Register the replacement action service
    component.async_register_entity_service(
        SERVICE_REPLACED, SERVICE_REPLACED_SCHEMA, "async_handle_replace_action"
    )

    return True

#async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
#    """Handle migration of a previous version config entry."""
#    _LOGGER.debug("Migrating from version %s", entry.version)
#    data = {**entry.data}
#    if entry.version == 1:
#        data.pop("login_response", None)
#        await hass.async_add_executor_job(_reauth_flow_wrapper, hass, data)
#        return False
#    if entry.version == 2:
#        await hass.async_add_executor_job(_reauth_flow_wrapper, hass, data)
#        return False
#    return True

async def async_setup_entry(hass, config_entry):
    """Set up this integration using UI."""
    if config_entry.source == config_entries.SOURCE_IMPORT:
        hass.async_create_task(hass.config_entries.async_remove(config_entry.entry_id))
        return False
    
    _LOGGER.warning("SETUP ENTRY '%s'", config_entry.data)

    # log startup message
    _LOGGER.info(
        CC_STARTUP_VERSION.format(name=DOMAIN, version=VERSION, issue_link=ISSUE_URL)
    )

    config_entry.options = config_entry.data
    config_entry.add_update_listener(update_listener)

    # Add sensor
    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup(config_entry, PLATFORM)
    )
    return True

async def async_remove_entry(hass, config_entry):
    """Handle removal of an entry."""
    _LOGGER.warning("REMOVE ENTRY '%s'", config_entry.data)

    try:
        await hass.config_entries.async_forward_entry_unload(config_entry, PLATFORM)
        _LOGGER.info(
            "Successfully removed sensor from the Replacements integration"
        )
    except ValueError:
        pass


async def update_listener(hass, entry):
    """Update listener."""
    entry.data = entry.options
    await hass.config_entries.async_forward_entry_unload(entry, PLATFORM)
    hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, PLATFORM))
