""" Constants """
from typing import Optional
import voluptuous as vol
from datetime import datetime
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_NAME


# Base component constants
DOMAIN = "replacements"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "4.5.0"
PLATFORM = "sensor"
ISSUE_URL = ""
ATTRIBUTION = "Sensor data calculated by Replace Sensor Integration"

ATTR_DATE = "date"
ATTR_DAYS_INTERVAL = "days_interval"
ATTR_DAYS_REMAINING = "days_remaining"

# Device classes
SENSOR_DEVICE_CLASS = "connectivity"

# Configuration
CONF_SENSOR = "sensor"
CONF_SENSORS = "sensors"
CONF_ENABLED = "enabled"
CONF_DATE = "date"
CONF_DATE_TEMPLATE = "date_template"
CONF_SOON = "days_as_soon"
CONF_ICON_NORMAL = "icon_normal"
CONF_ICON_SOON = "icon_soon"
CONF_ICON_TODAY = "icon_today"
CONF_ICON_EXPIRED = "icon_expired"
CONF_UNIT_OF_MEASUREMENT = "unit_of_measurement"
CONF_ID_PREFIX = "id_prefix"
CONF_DATE_EXCLUSION_ERROR = "Configuration cannot include both `date` and `date_template`. configure ONLY ONE"
CONF_DATE_REQD_ERROR = "Either `date` or `date_template` is Required"

# Defaults
DEFAULT_NAME = DOMAIN
DEFAULT_SOON = 3
DEFAULT_ICON_NORMAL = "mdi:calendar-blank"
DEFAULT_ICON_SOON = "mdi:calendar"
DEFAULT_ICON_TODAY = "mdi:calendar-star"
DEFAULT_ICON_EXPIRED = "mdi:calendar-remove"
DEFAULT_UNIT_OF_MEASUREMENT = "Days"
DEFAULT_ID_PREFIX = "replace_"

ICON = DEFAULT_ICON_NORMAL

def check_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        raise vol.Invalid(f"Invalid date: {value}")

DATE_SCHEMA = vol.Schema(
    {
        vol.Required(
            vol.Any(CONF_DATE,CONF_DATE_TEMPLATE,msg=CONF_DATE_REQD_ERROR)
        ): object
    }, extra=vol.ALLOW_EXTRA
)

SENSOR_CONFIG_SCHEMA = vol.All(
    vol.Schema(
        {
            vol.Required(CONF_NAME): cv.string,
            vol.Exclusive(CONF_DATE, CONF_DATE, msg=CONF_DATE_EXCLUSION_ERROR): check_date,
            vol.Exclusive(CONF_DATE_TEMPLATE, CONF_DATE, msg=CONF_DATE_EXCLUSION_ERROR): cv.string,
            vol.Optional(CONF_SOON, default=DEFAULT_SOON): cv.positive_int,
            vol.Optional(CONF_ICON_NORMAL, default=DEFAULT_ICON_NORMAL): cv.icon,
            vol.Optional(CONF_ICON_SOON, default=DEFAULT_ICON_SOON): cv.icon,
            vol.Optional(CONF_ICON_TODAY, default=DEFAULT_ICON_TODAY): cv.icon,
            vol.Optional(CONF_ICON_EXPIRED, default=DEFAULT_ICON_EXPIRED): cv.icon,
            vol.Optional(CONF_UNIT_OF_MEASUREMENT, default=DEFAULT_UNIT_OF_MEASUREMENT): cv.string,
            vol.Optional(CONF_ID_PREFIX, default=DEFAULT_ID_PREFIX): cv.string
        }
    )
)

SENSOR_SCHEMA = vol.All(SENSOR_CONFIG_SCHEMA, DATE_SCHEMA)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {vol.Optional(CONF_SENSORS): vol.All(cv.ensure_list, [SENSOR_SCHEMA])}
        )
    },
    extra=vol.ALLOW_EXTRA,
)
