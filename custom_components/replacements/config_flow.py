""" Config flow """
from __future__ import annotations

from copy import deepcopy
from turtle import update
from typing import Any

from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_UNIQUE_ID
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_registry import (
    async_entries_for_config_entry,
    async_get_registry,
)
import voluptuous as vol

from .const import (
    COMPONENT_NAME,
    CONF_ADD_ANOTHER,
    CONF_DAYS_INTERVAL,
    CONF_ICON_EXPIRED,
    CONF_ICON_NORMAL,
    CONF_ICON_SOON,
    CONF_ICON_TODAY,
    CONF_INTERVAL_EXCLUSION_ERROR,
    CONF_PREFIX,
    CONF_SOON,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_WEEKS_INTERVAL,
    DEFAULT_ICON_EXPIRED,
    DEFAULT_ICON_NORMAL,
    DEFAULT_ICON_SOON,
    DEFAULT_ICON_TODAY,
    DEFAULT_PREFIX,
    DEFAULT_SOON,
    DEFAULT_UNIT_OF_MEASUREMENT,
    DOMAIN,
    GROUP_INTERVAL,
)

ENTRY_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Optional(
            CONF_PREFIX, description={"suggested_value": DEFAULT_PREFIX}
        ): cv.string,
        vol.Exclusive(
            CONF_DAYS_INTERVAL, GROUP_INTERVAL, msg=CONF_INTERVAL_EXCLUSION_ERROR
        ): cv.positive_int,
        vol.Exclusive(
            CONF_WEEKS_INTERVAL, GROUP_INTERVAL, msg=CONF_INTERVAL_EXCLUSION_ERROR
        ): cv.positive_int,
        vol.Optional(CONF_SOON, default=DEFAULT_SOON): cv.positive_int,
        vol.Optional(
            CONF_UNIT_OF_MEASUREMENT, default=DEFAULT_UNIT_OF_MEASUREMENT
        ): cv.string,
        vol.Optional(CONF_ICON_NORMAL, default=DEFAULT_ICON_NORMAL): cv.string,
        vol.Optional(CONF_ICON_SOON, default=DEFAULT_ICON_SOON): cv.string,
        vol.Optional(CONF_ICON_TODAY, default=DEFAULT_ICON_TODAY): cv.string,
        vol.Optional(CONF_ICON_EXPIRED, default=DEFAULT_ICON_EXPIRED): cv.string,
        vol.Optional(CONF_ADD_ANOTHER): cv.boolean,
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(
            CONF_PREFIX, description={"suggested_value": DEFAULT_PREFIX}
        ): cv.string,
        vol.Exclusive(
            CONF_DAYS_INTERVAL, GROUP_INTERVAL, msg=CONF_INTERVAL_EXCLUSION_ERROR
        ): cv.positive_int,
        vol.Exclusive(
            CONF_WEEKS_INTERVAL, GROUP_INTERVAL, msg=CONF_INTERVAL_EXCLUSION_ERROR
        ): cv.positive_int,
        vol.Optional(CONF_SOON, default=DEFAULT_SOON): cv.positive_int,
        vol.Optional(
            CONF_UNIT_OF_MEASUREMENT, default=DEFAULT_UNIT_OF_MEASUREMENT
        ): cv.string,
        vol.Optional(CONF_ICON_NORMAL, default=DEFAULT_ICON_NORMAL): cv.string,
        vol.Optional(CONF_ICON_SOON, default=DEFAULT_ICON_SOON): cv.string,
        vol.Optional(CONF_ICON_TODAY, default=DEFAULT_ICON_TODAY): cv.string,
        vol.Optional(CONF_ICON_EXPIRED, default=DEFAULT_ICON_EXPIRED): cv.string,
        vol.Optional(CONF_ADD_ANOTHER): cv.boolean,
    }
)


def validate_soon(user_input=None):
    """Validate the 'interval' and 'soon' configurations.
    Specifically, the 'soon' parameter can never be lower
    than the 'interval'.

    Raises ValueError if 'soon' is lower than 'interval'
    """
    # Check if in days or weeks mode
    if CONF_DAYS_INTERVAL in user_input:
        if user_input[CONF_SOON] > user_input[CONF_DAYS_INTERVAL]:
            raise ValueError

    # We are in weeks mode
    else:
        if user_input[CONF_SOON] > user_input[CONF_WEEKS_INTERVAL]:
            raise ValueError


class ReplacementsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Replacements."""

    data: dict[str, Any] | None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return ReplacementsOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        """Create config entry. Show the setup form to the user."""
        errors = {}

        if user_input is not None:

            if not hasattr(self, "data"):
                self.data = {}
                self.data[DOMAIN] = []

            # Validate that the name hasn't been added already
            for replacement in self.data[DOMAIN]:
                if (CONF_NAME, user_input[CONF_NAME]) in replacement.items():
                    errors["base"] = "name_already_exists"

            if not errors:
                # Validate some parameters
                try:
                    validate_soon(user_input)
                except ValueError:
                    errors["base"] = "invalid_soon"

            if not errors:
                # Append the entry into the dictionary
                self.data[DOMAIN].append(user_input)

                # Check if the user checked the 'add another' box and show the form again
                if CONF_ADD_ANOTHER in user_input and user_input[CONF_ADD_ANOTHER]:
                    return await self.async_step_user()

                # User is done adding replacements, create the config entry
                return self.async_create_entry(title=COMPONENT_NAME, data=self.data)

        return self.async_show_form(
            step_id="user", data_schema=ENTRY_SCHEMA, errors=errors
        )

    # async def async_step_import(self, config: dict):  # pylint: disable=unused-argument
    #     """Import a config entry.
    #     Special type of import, we're not actually going to store any data.
    #     Instead, we're going to rely on the values that are in config file.
    #     """
    #     # if self._async_current_entries():
    #     #     return self.async_abort(reason="single_instance_allowed")
    #     return self.async_create_entry(title="configuration.yaml", data={})


class ReplacementsOptionsFlow(config_entries.OptionsFlow):
    """Replacements config flow options handler."""

    data: dict[str, Any] | None

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage the options."""
        errors: dict[str, str] = {}

        # Grab all configured replacements from the entity registry so we can populate the
        # multi-select dropdown that will allow a user to remove or edit the repalcement.
        entity_registry = await async_get_registry(self.hass)
        entries = async_entries_for_config_entry(
            entity_registry, self.config_entry.entry_id
        )

        # Default value for our multi-select.
        all_entities = {e.entity_id: e.original_name for e in entries}
        entity_map = {e.entity_id: e for e in entries}

        if user_input is not None:
            updated_entities = deepcopy(self.config_entry.data[DOMAIN])

            if not hasattr(self, "data"):
                self.data = {}
                self.data[DOMAIN] = []

            # Remove any unchecked replacements.
            removed_entities = [
                entity_id
                for entity_id in entity_map.keys()
                if entity_id not in user_input[DOMAIN]
            ]

            for entity_id in removed_entities:
                # Unregister from HA
                entity_registry.async_remove(entity_id)

                # Remove from our configured replacements
                entry = entity_map[entity_id]
                entry_id = entry.unique_id

                updated_entities = [
                    e for e in updated_entities if e[CONF_UNIQUE_ID] != entry_id
                ]

            if user_input.get(CONF_DAYS_INTERVAL) or user_input.get(
                CONF_WEEKS_INTERVAL
            ):

                # Validate some parameters
                try:
                    validate_soon(user_input)
                except ValueError:
                    errors["base"] = "invalid_soon"

                if not errors:
                    # Append the entry into the dictionary
                    user_input.pop(DOMAIN)
                    self.data[DOMAIN].append(user_input)

            # User is done adding replacements, create the config entry
            if not errors:
                self.data[DOMAIN] = self.data[DOMAIN] + updated_entities
                return self.async_create_entry(title=COMPONENT_NAME, data=self.data)

        # Create a schema with the list of all configured entities
        remove_schema = vol.Schema(
            {
                vol.Optional(
                    DOMAIN, default=list(all_entities.keys())
                ): cv.multi_select(all_entities),
            },
            extra=vol.ALLOW_EXTRA,
        )

        # Extend the remove schema with the add
        options_schema = remove_schema.extend(OPTIONS_SCHEMA.schema)

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )
