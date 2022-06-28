"""The Replacements integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLATFORM, STARTUP_MESSAGE

_LOGGER = logging.getLogger(__name__)


# async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
#     """Handle migration of a previous version config entry."""
#     _LOGGER.debug("Migrating from version %s", entry.version)
#     data = {**entry.data}
#     if entry.version == 1:
#         data.pop("login_response", None)
#         await hass.async_add_executor_job(_reauth_flow_wrapper, hass, data)
#         return False
#     if entry.version == 2:
#         await hass.async_add_executor_job(_reauth_flow_wrapper, hass, data)
#         return False
#     return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    # Get the integration reference inside hass
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    # Store the entry under our domain to allow multiple entries
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Forward the setup to the platform
    hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, PLATFORM))

    entry.async_on_unload(entry.add_update_listener(config_entry_update_listener))
    return True


async def config_entry_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener, called when the config entry options are changed."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORM):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
