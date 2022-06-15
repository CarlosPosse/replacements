"""The Replacements integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, ISSUE_URL, PLATFORM, STARTUP_MESSAGE, VERSION

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up a replacement from YAML."""

    # Get the integration reference inside hass
    # hass.data[DOMAIN] = EntityComponent(_LOGGER, DOMAIN, hass)
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    if DOMAIN not in config:
        return True

    ## Setup all entities in yaml

    # Load every platform in the main loop (calls async_setup_platform)
    for entry in config[DOMAIN].items():
        _LOGGER.debug("Setup %s.%s", DOMAIN, entry)

        hass.async_create_task(
            discovery.async_load_platform(hass, PLATFORM, DOMAIN, entry, config)
        )

    #     # Import all the yaml entries to the UI as well
    #     hass.async_create_task(
    #         hass.config_entries.flow.async_init(
    #             DOMAIN, context={"source": SOURCE_IMPORT}, data=config
    #         )
    #     )

    # Setup has been successful
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
    ## TODO: This imports
    # if entry.source == config_entries.SOURCE_IMPORT:
    #     hass.async_create_task(hass.config_entries.async_remove(entry.entry_id))
    #     return False

    # Store the entry under our domain to allow multiple entries
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Forward the setup to the platform
    hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, PLATFORM))

    # entry.async_on_unload(entry.add_update_listener(config_entry_update_listener))
    return True


# async def config_entry_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
#     """Update listener, called when the config entry options are changed."""
#     await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORM):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


# async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
#     """Update listener."""
#     await hass.config_entries.async_reload(entry.entry_id)
