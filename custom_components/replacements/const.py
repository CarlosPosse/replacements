""" Constants """
from datetime import datetime
from typing import Optional

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import CONF_NAME
from homeassistant.helpers.config_validation import make_entity_service_schema

# Integration definitions
VERSION = "0.1.0"
DOMAIN = "replacements"
DOMAIN_DATA = f"{DOMAIN}_data"
PLATFORM = "sensor"
ISSUE_URL = "https://img.shields.io/github/issues/carlosposse/Replacements"
ATTRIBUTION = "Data calculated by Replacements Integration"

# Configuration
CONF_SENSORS = "sensors"
CONF_DAYS_INTERVAL = "days_interval"
CONF_WEEKS_INTERVAL = "weeks_interval"
CONF_SOON = "soon_interval"
CONF_ICON_NORMAL = "icon_normal"
CONF_ICON_SOON = "icon_soon"
CONF_ICON_TODAY = "icon_today"
CONF_ICON_EXPIRED = "icon_expired"
CONF_UNIT_OF_MEASUREMENT = "unit_of_measurement"
CONF_ID_PREFIX = "id_prefix"

# Extra attributes
ATTR_DATE = "date"
ATTR_DAYS_INTERVAL = "days_interval"
ATTR_WEEKS_INTERVAL = "weeks_interval"
ATTR_SOON = "soon"
ATTR_STOCK = "stock"

# Services
SERVICE_STOCK = "renew_stock"
SERVICE_STOCK_SCHEMA = make_entity_service_schema({
        vol.Required("new_stock"): int
    })
SERVICE_DATE = "set_date"
SERVICE_DATE_SCHEMA = make_entity_service_schema({
        vol.Required("new_date"): cv.string
    })
SERVICE_REPLACED = "replace_action"
SERVICE_REPLACED_SCHEMA = make_entity_service_schema({})

# Defaults
DEFAULT_SOON = 1
DEFAULT_ICON_NORMAL = "mdi:calendar-blank"
DEFAULT_ICON_SOON = "mdi:calendar"
DEFAULT_ICON_TODAY = "mdi:calendar-star"
DEFAULT_ICON_EXPIRED = "mdi:calendar-remove"
DEFAULT_UNIT_OF_MEASUREMENT = "Days"
DEFAULT_ID_PREFIX = "replace_"

# Schema Exclusions
GROUP_INTERVAL = "interval"

CONF_INTERVAL_EXCLUSION_ERROR = "Configuration cannot include both `days_interval` and `weeks_interval`. configure ONLY ONE"
CONF_INTERVAL_REQD_ERROR = "Either `days_interval` or `weeks_interval` is Required"

# Schema definitions
INTERVAL_SCHEMA = vol.Schema(
    {
        vol.Required(
            vol.Any(CONF_DAYS_INTERVAL, CONF_WEEKS_INTERVAL, msg=CONF_INTERVAL_REQD_ERROR)
        ): object,
    }, extra=vol.ALLOW_EXTRA
)

SENSOR_CONFIG_SCHEMA = vol.All(
    vol.Schema(
        {
            vol.Required(CONF_NAME): cv.string,
            vol.Exclusive(CONF_DAYS_INTERVAL, GROUP_INTERVAL, msg=CONF_INTERVAL_EXCLUSION_ERROR): cv.positive_int,
            vol.Exclusive(CONF_WEEKS_INTERVAL, GROUP_INTERVAL, msg=CONF_INTERVAL_EXCLUSION_ERROR): cv.positive_int,
            vol.Optional(CONF_SOON, DEFAULT_SOON): cv.positive_int,
            vol.Optional(CONF_ICON_NORMAL, default=DEFAULT_ICON_NORMAL): cv.icon,
            vol.Optional(CONF_ICON_SOON, default=DEFAULT_ICON_SOON): cv.icon,
            vol.Optional(CONF_ICON_TODAY, default=DEFAULT_ICON_TODAY): cv.icon,
            vol.Optional(CONF_ICON_EXPIRED, default=DEFAULT_ICON_EXPIRED): cv.icon,
            vol.Optional(CONF_UNIT_OF_MEASUREMENT, default=DEFAULT_UNIT_OF_MEASUREMENT): cv.string,
            vol.Optional(CONF_ID_PREFIX, default=DEFAULT_ID_PREFIX): cv.string
        }
    )
)

SENSOR_SCHEMA = vol.All(SENSOR_CONFIG_SCHEMA, INTERVAL_SCHEMA)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {vol.Optional(CONF_SENSORS): vol.All(cv.ensure_list, [SENSOR_SCHEMA])}
        )
    },
    extra=vol.ALLOW_EXTRA,
)
