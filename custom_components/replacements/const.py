""" Constants """
import voluptuous as vol

from homeassistant.const import CONF_NAME, CONF_PREFIX, CONF_UNIT_OF_MEASUREMENT
from homeassistant.helpers import config_validation as cv

# Integration definitions
COMPONENT_NAME = "Replacements"
DOMAIN = "replacements"
PLATFORM = "sensor"
VERSION = "1.0.0"

DOMAIN_DATA = f"{DOMAIN}_data"
ISSUE_URL = "https://github.com/carlosposse/Replacements/issues"
ATTRIBUTION = "Data calculated by Replacements Integration"

# Basic Configuration
CONF_DAYS_INTERVAL = "days_interval"
CONF_WEEKS_INTERVAL = "weeks_interval"
CONF_SOON = "soon_interval"
CONF_ICON_NORMAL = "icon_normal"
CONF_ICON_SOON = "icon_soon"
CONF_ICON_TODAY = "icon_today"
CONF_ICON_EXPIRED = "icon_expired"

# Config Flow Configuration
CONF_ADD_ANOTHER = "add_another"

# Defaults
DEFAULT_SOON = 1
DEFAULT_ICON_NORMAL = "mdi:calendar-blank"
DEFAULT_ICON_SOON = "mdi:calendar"
DEFAULT_ICON_TODAY = "mdi:calendar-star"
DEFAULT_ICON_EXPIRED = "mdi:calendar-remove"
DEFAULT_UNIT_OF_MEASUREMENT = "Days"
DEFAULT_PREFIX = "replace_"

# Schema Exclusions
GROUP_INTERVAL = "interval"

CONF_INTERVAL_EXCLUSION_ERROR = "Configuration cannot include both `days_interval` and `weeks_interval`. configure ONLY ONE"
CONF_INTERVAL_REQD_ERROR = "Either `days_interval` or `weeks_interval` is Required"

# Schema definitions
INTERVAL_SCHEMA = vol.Schema(
    {
        vol.Required(
            vol.Any(
                CONF_DAYS_INTERVAL, CONF_WEEKS_INTERVAL, msg=CONF_INTERVAL_REQD_ERROR
            )
        ): object,
    },
    extra=vol.ALLOW_EXTRA,
)

REPLACEMENT_CONFIG_SCHEMA = vol.Schema(
    vol.All(
        {
            vol.Exclusive(
                CONF_DAYS_INTERVAL, GROUP_INTERVAL, msg=CONF_INTERVAL_EXCLUSION_ERROR
            ): cv.positive_int,
            vol.Exclusive(
                CONF_WEEKS_INTERVAL, GROUP_INTERVAL, msg=CONF_INTERVAL_EXCLUSION_ERROR
            ): cv.positive_int,
            vol.Optional(CONF_NAME): cv.string,
            vol.Optional(CONF_SOON, default=DEFAULT_SOON): cv.positive_int,
            vol.Optional(CONF_ICON_NORMAL, default=DEFAULT_ICON_NORMAL): cv.icon,
            vol.Optional(CONF_ICON_SOON, default=DEFAULT_ICON_SOON): cv.icon,
            vol.Optional(CONF_ICON_TODAY, default=DEFAULT_ICON_TODAY): cv.icon,
            vol.Optional(CONF_ICON_EXPIRED, default=DEFAULT_ICON_EXPIRED): cv.icon,
            vol.Optional(
                CONF_UNIT_OF_MEASUREMENT, default=DEFAULT_UNIT_OF_MEASUREMENT
            ): cv.string,
            vol.Optional(CONF_PREFIX, default=DEFAULT_PREFIX): cv.string,
        }
    )
)

REPLACEMENT_SCHEMA = vol.All(REPLACEMENT_CONFIG_SCHEMA, INTERVAL_SCHEMA)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema({cv.slug: vol.All(cv.ensure_list, [REPLACEMENT_SCHEMA])})},
    extra=vol.ALLOW_EXTRA,
)
