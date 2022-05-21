""" Config flow """
import uuid
from collections import OrderedDict
from datetime import datetime

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback

from .const import (CONF_ICON_EXPIRED, CONF_ICON_NORMAL, CONF_ICON_SOON,
                    CONF_ICON_TODAY, CONF_ID_PREFIX, CONF_UNIT_OF_MEASUREMENT,
                    DEFAULT_ICON_EXPIRED, DEFAULT_ICON_NORMAL,
                    DEFAULT_ICON_SOON, DEFAULT_ICON_TODAY, DEFAULT_ID_PREFIX,
                    DEFAULT_UNIT_OF_MEASUREMENT, DOMAIN)


@config_entries.HANDLERS.register(DOMAIN)
class ReplacementsFlowHandler(config_entries.ConfigFlow):
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        self._errors = {}
        self._data = {}
        self._data["unique_id"] = str(uuid.uuid4())

    async def async_step_user(self, user_input=None):   # pylint: disable=unused-argument
        self._errors = {}
        if user_input is not None:
            self._data.update(user_input)
            if self._errors == {}:
                self.init_info = user_input
                return await self.async_step_icons()
        
        return await self._show_user_form(user_input)

    async def async_step_icons(self, user_input=None):
        self._errors = {}
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title=self._data["name"], data=self._data)
        
        return await self._show_icon_form(user_input)

    async def _show_user_form(self, user_input):
        name = ""
        date = ""
        unit_of_measurement = DEFAULT_UNIT_OF_MEASUREMENT
        id_prefix = DEFAULT_ID_PREFIX

        if user_input is not None:
            if CONF_NAME in user_input:
                name = user_input[CONF_NAME]
            if CONF_UNIT_OF_MEASUREMENT in user_input:
                unit_of_measurement = user_input[CONF_UNIT_OF_MEASUREMENT]
            if CONF_ID_PREFIX in user_input:
                id_prefix = user_input[CONF_ID_PREFIX]
        
        data_schema = OrderedDict()
        data_schema[vol.Required(CONF_NAME, default=name)] = str
        data_schema[vol.Required(CONF_UNIT_OF_MEASUREMENT, default=unit_of_measurement)] = str
        data_schema[vol.Optional(CONF_ID_PREFIX, default=id_prefix)] = str

        return self.async_show_form(step_id="user", data_schema=vol.Schema(data_schema), errors=self._errors)

    async def _show_icon_form(self, user_input):
        icon_normal = DEFAULT_ICON_NORMAL
        icon_soon = DEFAULT_ICON_SOON
        icon_today = DEFAULT_ICON_TODAY
        icon_expired = DEFAULT_ICON_EXPIRED

        if user_input is not None:
            if CONF_ICON_NORMAL in user_input:
                icon_normal = user_input[CONF_ICON_NORMAL]
            if CONF_ICON_SOON in user_input:
                icon_soon = user_input[CONF_ICON_SOON]
            if CONF_ICON_TODAY in user_input:
                icon_today = user_input[CONF_ICON_TODAY]
            if CONF_ICON_EXPIRED in user_input:
                icon_expired = user_input[CONF_ICON_EXPIRED]
        
        data_schema = OrderedDict()
        data_schema[vol.Required(CONF_ICON_NORMAL, default=icon_normal)] = str
        data_schema[vol.Required(CONF_ICON_SOON, default=icon_soon)] = str
        data_schema[vol.Required(CONF_ICON_TODAY, default=icon_today)] = str
        data_schema[vol.Required(CONF_ICON_EXPIRED, default=icon_expired)] = str

        return self.async_show_form(step_id="icons", data_schema=vol.Schema(data_schema), errors=self._errors)

    async def async_step_import(self, user_input):  # pylint: disable=unused-argument
        """Import a config entry.
        Special type of import, we're not actually going to store any data.
        Instead, we're going to rely on the values that are in config file.
        """
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        return self.async_create_entry(title="configuration.yaml", data={})

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        if config_entry.options.get("unique_id", None) is not None:
            return OptionsFlowHandler(config_entry)
        else:
            return EmptyOptions(config_entry)

def is_not_date(date):
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return False
    except ValueError:
        return True


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry
        self._data = {}
        self._data["unique_id"] = config_entry.options.get("unique_id")

    async def async_step_init(self, user_input=None):
        self._errors = {}
        if user_input is not None:
            self._data.update(user_input)
            if self._errors == {}:
                return await self.async_step_icons()
        return await self._show_init_form(user_input)

    async def async_step_icons(self, user_input=None):
        self._errors = {}
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="", data=self._data)
        return await self._show_icon_form(user_input)

    async def _show_init_form(self, user_input):
        data_schema = OrderedDict()
        unit_of_measurement = self.config_entry.options.get(CONF_UNIT_OF_MEASUREMENT)
        if unit_of_measurement is None:
            unit_of_measurement = DEFAULT_UNIT_OF_MEASUREMENT

        data_schema[vol.Required(CONF_NAME,default=self.config_entry.options.get(CONF_NAME),)] = str
        data_schema[vol.Required(CONF_UNIT_OF_MEASUREMENT,default=unit_of_measurement,)] = str

        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(data_schema), errors=self._errors
        )

    async def _show_icon_form(self, user_input):
        data_schema = OrderedDict()
        data_schema[vol.Required(CONF_ICON_NORMAL,default=self.config_entry.options.get(CONF_ICON_NORMAL),)] = str
        data_schema[vol.Required(CONF_ICON_SOON,default=self.config_entry.options.get(CONF_ICON_SOON),)] = str
        data_schema[vol.Required(CONF_ICON_TODAY,default=self.config_entry.options.get(CONF_ICON_TODAY),)] = str
        data_schema[vol.Required(CONF_ICON_EXPIRED,default=self.config_entry.options.get(CONF_ICON_EXPIRED),)] = str
        return self.async_show_form(step_id="icons", data_schema=vol.Schema(data_schema), errors=self._errors)


class EmptyOptions(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry
