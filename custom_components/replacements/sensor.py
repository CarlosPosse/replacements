"""Platform for sensor integration."""
from dateutil.relativedelta import relativedelta
from datetime import datetime, date

from homeassistant.helpers.entity import Entity, generate_entity_id
from homeassistant.components.sensor import ENTITY_ID_FORMAT
from homeassistant.helpers import template as templater
import homeassistant.util.dt as dt_util

from homeassistant.const import (
    CONF_NAME,
    ATTR_ATTRIBUTION,
)

from .const import (
    ATTRIBUTION,
    DEFAULT_UNIT_OF_MEASUREMENT,
    CONF_SOON,
    CONF_ICON_NORMAL,
    CONF_ICON_SOON,
    CONF_ICON_TODAY,
    CONF_ICON_EXPIRED,
    CONF_DATE,
    CONF_DATE_TEMPLATE,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_ID_PREFIX
)

ATTR_DAYS_INTERVAL = "days_interval"
ATTR_DAYS_REMAINING = "days_remaining"
ATTR_DATE = "date"

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup the sensor platform."""
    async_add_entities([ReplaceSensor(hass, discovery_info)], True)

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor platform."""
    async_add_devices([ReplaceSensor(hass, config_entry.data)], True)

def validate_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return "Invalid Date"

class ReplaceSensor(Entity):
    def __init__(self, hass, config):
        """Initialize the sensor."""
        # Initialize the configuration and entity
        self.config = config
        self._name = config.get(CONF_NAME)
        self._id_prefix = config.get(CONF_ID_PREFIX)
        if self._id_prefix is None:
            self._id_prefix = "replace_"
        self.entity_id = generate_entity_id(ENTITY_ID_FORMAT, self._id_prefix + self._name, [])

        # Initialize date variables
        self._date = ""
        self._template_sensor = False
        self._date_template = config.get(CONF_DATE_TEMPLATE)
        if self._date_template is not None:
            self._template_sensor = True
        else:
            self._date = validate_date(config.get(CONF_DATE))
            self._date = self._date.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
        
        # Initialize the icons
        self._icon_normal = config.get(CONF_ICON_NORMAL)
        self._icon_soon = config.get(CONF_ICON_SOON)
        self._icon_today = config.get(CONF_ICON_TODAY)
        self._icon_expired = config.get(CONF_ICON_EXPIRED)
        self._icon = self._icon_normal

        # Initialize everything else
        self._state = 0
        self._soon = config.get(CONF_SOON)
        self._days_interval = 0
        self._days_remaining = 0
        self._unit_of_measurement = config.get(CONF_UNIT_OF_MEASUREMENT)
        if self._unit_of_measurement is None:
            self._unit_of_measurement = DEFAULT_UNIT_OF_MEASUREMENT

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return self.config.get("unique_id", None)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the name of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        res = {}
        res[ATTR_ATTRIBUTION] = ATTRIBUTION
        if self._state in ["Invalid Date", "Invalid Template"]:
            return res
        res[ATTR_DAYS_INTERVAL] = self._days_interval
        res[ATTR_DAYS_REMAINING] = self._days_remaining
        res[ATTR_DATE] = self._date
        return res

    @property
    def icon(self):
        return self._icon

    @property
    def unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        if self._state in ["Invalid Date", "Invalid Template"]:
            return
        return self._unit_of_measurement

    async def async_update(self):
        """update the sensor"""

        # Check if we're using a template for the date and process
        if self._template_sensor:
            try:
                template_date = templater.Template(self._date_template, self.hass).async_render()
                self._date = validate_date(template_date)
                self._date = self._date.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
            except:
                self._state = "Invalid Template"
                return
            if self._date == "Invalid Date":
                self._state = self._date
                return

        # Get today's date and calculate remaining days
        today = date.today()
        daysRemaining = (self._date.date() - today).days
        
        # Assign icon according to number of days remaining
        if daysRemaining < 0:
            self._icon = self._icon_expired
        elif daysRemaining == 0:
            self._icon = self._icon_today
        elif daysRemaining <= self._soon:
            self._icon = self._icon_soon
        else:
            self._icon = self._icon_normal

        # Update internal state and variables
        self._state = daysRemaining
        self._days_remaining = daysRemaining
