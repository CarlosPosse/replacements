"""Platform for sensor integration."""
import logging
from datetime import date, datetime

import homeassistant.util.dt as dt_util
from dateutil.relativedelta import relativedelta
from homeassistant.components.sensor import ENTITY_ID_FORMAT
from homeassistant.const import ATTR_ATTRIBUTION, CONF_ID, CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import template as templater
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity, generate_entity_id
from homeassistant.helpers.restore_state import ExtraStoredData, RestoreEntity

from .const import (ATTR_DATE, ATTR_DAYS_INTERVAL, ATTR_SOON, ATTR_STOCK,
                    ATTR_WEEKS_INTERVAL, ATTRIBUTION, CONF_DAYS_INTERVAL,
                    CONF_ICON_EXPIRED, CONF_ICON_NORMAL, CONF_ICON_SOON,
                    CONF_ICON_TODAY, CONF_ID_PREFIX, CONF_SOON,
                    CONF_UNIT_OF_MEASUREMENT, CONF_WEEKS_INTERVAL,
                    DEFAULT_SOON, DEFAULT_UNIT_OF_MEASUREMENT)

ATTR_WEEKS_INTERVAL = "weeks_interval"

DATA_UPDATED = "replacements_updated"
INVALID_DATE = "Invalid Date"

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup the sensor platform."""
    _LOGGER.warning("SETUP PLATFORM")
    async_add_entities([Replacement(hass, discovery_info)], True)

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup an entry."""
    # Instantiate device and add to the platform
    async_add_devices([Replacement(hass, config_entry.data)], True)

def validate_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        pass
    try:
        _LOGGER.warning("Pass as value")
        return value
    except ValueError:
        _LOGGER.warning("Date value error")
        return INVALID_DATE
    except AttributeError:
        _LOGGER.warning("Date attribute error")
        return INVALID_DATE


class Replacement(RestoreEntity):

    def __init__(self, hass, config):
        """Initialize the sensor."""
        self._hass = hass
        self._config: dict = config

        # Initialize the configuration and entity
        self._name = config.get(CONF_NAME)
        self._id_prefix = config.get(CONF_ID_PREFIX)
        if self._id_prefix is None:
            self._id_prefix = "replace_"
        self.entity_id = generate_entity_id(ENTITY_ID_FORMAT, self._id_prefix + self._name, [])

        # Get required configuration
        self._days_interval = config.get(CONF_DAYS_INTERVAL)
        self._weeks_interval = config.get(CONF_DAYS_INTERVAL)

        # Define if we are in week or day mode
        if self._days_interval is None:
            self._days_mode = False
        else:
            self._days_mode = True

        # Initialize everything else
        self._days_remaining = 0
        self._soon = config.get(CONF_SOON)
        self._date = INVALID_DATE
        self._stock = 0
        self._unit_of_measurement = config.get(CONF_UNIT_OF_MEASUREMENT)
        if self._unit_of_measurement is None:
            self._unit_of_measurement = DEFAULT_UNIT_OF_MEASUREMENT

        # Initialize the icons
        self._icon_normal = config.get(CONF_ICON_NORMAL)
        self._icon_soon = config.get(CONF_ICON_SOON)
        self._icon_today = config.get(CONF_ICON_TODAY)
        self._icon_expired = config.get(CONF_ICON_EXPIRED)
        self._icon = self._icon_normal

    def _calculate_new_date(self):
        _LOGGER.warning("Calculate new date")

        # Calculate the new date according to the interval
        if self._days_mode:
            nextDate = date.today() + relativedelta(days=self._days_interval)
        else:
            nextDate = date.today() + relativedelta(weeks=self._weeks_interval)
        
        # Replace new date with datetime
        self._date = datetime(nextDate.year, nextDate.month, nextDate.day)
        _LOGGER.warning("New date %s", self._date)

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        # If variable state have been saved.
        state = await self.async_get_last_state()
        if state:
            # Restore state
            self._days_remaining = state.state

            # Restore date
            if ATTR_DATE in state.attributes:
                if not state.attributes[ATTR_DATE] == INVALID_DATE:
                    self._date = datetime.strptime(state.attributes[ATTR_DATE], '%Y-%m-%dT%H:%M:%S')

            # If date is invalid, assign to the next interval
            if self._date == INVALID_DATE:
                self._calculate_new_date()

            # Restore stock
            if ATTR_STOCK in state.attributes: 
                _LOGGER.warning("Restoring stock '%d'", state.attributes[ATTR_STOCK])
                self._stock = state.attributes[ATTR_STOCK]
        
        # Schedule an immediate update
        async_dispatcher_connect(
            self._hass, DATA_UPDATED, self._schedule_immediate_update
        )

    @callback
    def _schedule_immediate_update(self):
        self.async_schedule_update_ha_state(True)

    #@property
    #def unique_id(self):
    #    """Return a unique ID to use for this sensor."""
    #    _LOGGER.warning("UNIQUE ID '%s'", self._config.get("unique_id", None))
    #    return self._config.get("unique_id", None)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._days_remaining

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        res = {}
        res[ATTR_ATTRIBUTION] = ATTRIBUTION
        
        # Return the interval according to the mode
        if self._days_mode:
            res[ATTR_DAYS_INTERVAL] = self._days_interval
        else:
            res[ATTR_WEEKS_INTERVAL] = self._weeks_interval

        # Return all other attributes
        res[ATTR_DATE] = self._date
        res[ATTR_SOON] = self._soon
        res[ATTR_STOCK] = self._stock
        return res

    @property
    def icon(self):
        return self._icon

    @property
    def unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        return self._unit_of_measurement

    async def async_handle_renew_stock(self, new_stock=-1) -> None:
        _LOGGER.warning("RENEW STOCK")
        self._stock = stock
        await self.async_update_ha_state()

    async def async_handle_set_date(self, new_date=None) -> None:
        _LOGGER.warning("SET DATE")
        await self.async_update_ha_state()

    async def async_handle_replace_action(self) -> None:
        _LOGGER.warning("REPLACE ACTION")

        # Calculate new date
        self._calculate_new_date()

        # Decrement the stock
        self._stock = self._stock - 1

        # Update the core state
        await self.async_update_ha_state()

    async def async_update(self):
        """update the sensor"""

        # Check for invalid date when initializing
        if self._date == INVALID_DATE:
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

        # Update internal state
        self._days_remaining = daysRemaining
