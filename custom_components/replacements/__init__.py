"""The Replacements integration."""
import logging

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, ISSUE_URL, PLATFORM, VERSION

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up a replacement from YAML."""

    # # Get the integration reference inside hass
    # hass.data[DOMAIN] = EntityComponent(_LOGGER, DOMAIN, hass)

    # ## Setup all entities in yaml

    # # Load every platform in the main loop (calls async_setup_platform)
    # for entry in config[DOMAIN].items():
    #     _LOGGER.debug("Setup %s.%s", DOMAIN, entry)

    #     hass.async_create_task(
    #         discovery.async_load_platform(hass, PLATFORM, DOMAIN, entry, config)
    #     )

    # # Import all the yaml entries to the UI as well
    # hass.async_create_task(
    #     hass.config_entries.flow.async_init(
    #         DOMAIN, context={"source": SOURCE_IMPORT}, data=config
    #     )
    # )

    # # Setup has been successful
    return True


# async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
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


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    # if entry.source == config_entries.SOURCE_IMPORT:
    #     hass.async_create_task(hass.config_entries.async_remove(entry.entry_id))
    #     return False

    _LOGGER.warning("SETUP ENTRY '%s'", entry.data)

    # Store the entry under our domain to allow multiple entries
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Forward the setup to the platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, PLATFORM)
    )
    return True


# async def async_remove_entry(hass, config_entry):
#     """Handle removal of an entry."""
#     _LOGGER.warning("REMOVE ENTRY '%s'", config_entry.data)

#     try:
#         await hass.config_entries.async_forward_entry_unload(config_entry, PLATFORM)
#         _LOGGER.info("Successfully removed sensor from the Replacements integration")
#     except ValueError:
#         pass


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener."""
    await hass.config_entries.async_reload(entry.entry_id)
