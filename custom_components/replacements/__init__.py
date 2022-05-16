"""The replacements integration."""
import logging

# from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.typing import ConfigType
from integrationhelper.const import CC_STARTUP_VERSION

from .const import DOMAIN, ISSUE_URL, PLATFORM, VERSION

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up a replacement from YAML."""

    # Get the integration reference inside hass
    component = hass.data[DOMAIN] = EntityComponent(_LOGGER, DOMAIN, hass)

    # Make sure domain is declared in configuration.yaml
    if DOMAIN not in config:
        return True

    # Log startup message
    _LOGGER.info(
        CC_STARTUP_VERSION.format(name=DOMAIN, version=VERSION, issue_link=ISSUE_URL)
    )

    ## Setup all entities in yaml

    # Load every platform in the main loop (calls async_setup_platform)
    for entry in config[DOMAIN].items():
        _LOGGER.debug("Setup %s.%s", DOMAIN, entry)

        hass.async_create_task(
            discovery.async_load_platform(
                hass,
                PLATFORM,
                DOMAIN,
                entry,
                config
            )
        )
        
    # # Setup all entities in UI
    # hass.async_create_task(
    #     hass.config_entries.flow.async_init(
    #         DOMAIN, context={"source": config_entries.SOURCE_IMPORT}, data={}
    #     )
    # )

    # Setup has been successful
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

# async def async_setup_entry(hass, config_entry):
#     """Set up this integration using UI."""
#     if config_entry.source == config_entries.SOURCE_IMPORT:
#         hass.async_create_task(hass.config_entries.async_remove(config_entry.entry_id))
#         return False
    
#     _LOGGER.warning("SETUP ENTRY '%s'", config_entry.data)

#     # log startup message
#     _LOGGER.info(
#         CC_STARTUP_VERSION.format(name=DOMAIN, version=VERSION, issue_link=ISSUE_URL)
#     )

#     config_entry.options = config_entry.data
#     config_entry.add_update_listener(update_listener)

#     # Add sensor
#     hass.async_add_job(
#         hass.config_entries.async_forward_entry_setup(config_entry, PLATFORM)
#     )
#     return True

# async def async_remove_entry(hass, config_entry):
#     """Handle removal of an entry."""
#     _LOGGER.warning("REMOVE ENTRY '%s'", config_entry.data)

#     try:
#         await hass.config_entries.async_forward_entry_unload(config_entry, PLATFORM)
#         _LOGGER.info(
#             "Successfully removed sensor from the Replacements integration"
#         )
#     except ValueError:
#         pass


# async def update_listener(hass, entry):
#     """Update listener."""
#     entry.data = entry.options
#     await hass.config_entries.async_forward_entry_unload(entry, PLATFORM)
#     hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, PLATFORM))
