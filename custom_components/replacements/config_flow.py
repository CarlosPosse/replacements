""" Config flow """
from __future__ import annotations
from collections import OrderedDict
from typing import Any

# from datetime import datetime

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_UNIQUE_ID
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import (
    COMPONENT_NAME,
    DOMAIN,
    CONF_DAYS_INTERVAL,
    CONF_WEEKS_INTERVAL,
    CONF_SOON,
    CONF_PREFIX,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_ICON_EXPIRED,
    CONF_ICON_NORMAL,
    CONF_ICON_SOON,
    CONF_ICON_TODAY,
    DEFAULT_SOON,
    DEFAULT_PREFIX,
    DEFAULT_UNIT_OF_MEASUREMENT,
    DEFAULT_ICON_NORMAL,
    DEFAULT_ICON_SOON,
    DEFAULT_ICON_TODAY,
    DEFAULT_ICON_EXPIRED,
    CONF_ADD_ANOTHER,
    GROUP_INTERVAL,
    CONF_INTERVAL_EXCLUSION_ERROR,
)

DATA_SCHEMA = vol.Schema(
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
                self.data = user_input
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
                if user_input[CONF_ADD_ANOTHER]:
                    return await self.async_step_user()

                # User is done adding replacements, create the config entry
                return self.async_create_entry(title=COMPONENT_NAME, data=self.data)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
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
    """Handle options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry
        # self._data = {}
        # self._data["unique_id"] = config_entry.options.get("unique_id")

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(step_id="init", data_schema=self._get_init_schema())

    # async def async_step_icons(self, user_input=None):
    #     self._errors = {}
    #     if user_input is not None:
    #         self._data.update(user_input)
    #         return self.async_create_entry(title="", data=self._data)
    #     return await self._show_icon_form(user_input)

    async def _get_init_schema(self):
        data_schema = OrderedDict()
        unit_of_measurement = self.config_entry.options.get(CONF_UNIT_OF_MEASUREMENT)
        if unit_of_measurement is None:
            unit_of_measurement = DEFAULT_UNIT_OF_MEASUREMENT

        data_schema[
            vol.Required(
                CONF_NAME,
                default=self.config_entry.options.get(CONF_NAME),
            )
        ] = str
        data_schema[
            vol.Required(
                CONF_UNIT_OF_MEASUREMENT,
                default=unit_of_measurement,
            )
        ] = str

        return vol.Schema(data_schema)

    # async def _get_icon_schema(self, user_input):
    #     data_schema = OrderedDict()
    #     data_schema[
    #         vol.Required(
    #             CONF_ICON_NORMAL,
    #             default=self.config_entry.options.get(CONF_ICON_NORMAL),
    #         )
    #     ] = str
    #     data_schema[
    #         vol.Required(
    #             CONF_ICON_SOON,
    #             default=self.config_entry.options.get(CONF_ICON_SOON),
    #         )
    #     ] = str
    #     data_schema[
    #         vol.Required(
    #             CONF_ICON_TODAY,
    #             default=self.config_entry.options.get(CONF_ICON_TODAY),
    #         )
    #     ] = str
    #     data_schema[
    #         vol.Required(
    #             CONF_ICON_EXPIRED,
    #             default=self.config_entry.options.get(CONF_ICON_EXPIRED),
    #         )
    #     ] = str
    #     return self.async_show_form(
    #         step_id="icons", data_schema=vol.Schema(data_schema), errors=self._errors
    #     )
