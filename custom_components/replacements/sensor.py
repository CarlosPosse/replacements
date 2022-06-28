"""Platform for sensor integration."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import InvalidOperation
import logging
from typing import Any

from dateutil.relativedelta import relativedelta
from homeassistant import config_entries
from homeassistant.components.sensor import RestoreSensor, SensorExtraStoredData
from homeassistant.const import (
    ATTR_DATE,
    CONF_NAME,
    CONF_UNIQUE_ID,
    CONF_UNIT_OF_MEASUREMENT,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_platform
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.config_validation import make_entity_service_schema
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
import homeassistant.util.dt as dt_util
import voluptuous as vol

from .const import (
    CONF_DAYS_INTERVAL,
    CONF_ICON_EXPIRED,
    CONF_ICON_NORMAL,
    CONF_ICON_SOON,
    CONF_ICON_TODAY,
    CONF_PREFIX,
    CONF_SOON,
    CONF_WEEKS_INTERVAL,
    DOMAIN,
    PLATFORM,
)

_LOGGER = logging.getLogger(__name__)

# Attributes
ATTR_DAYS_INTERVAL = "days_interval"
ATTR_WEEKS_INTERVAL = "weeks_interval"
ATTR_SOON = "soon"
ATTR_STOCK = "stock"
ATTR_NEW_DATE = "new_date"

# Services
SERVICE_STOCK = "renew_stock"
SERVICE_STOCK_SCHEMA = make_entity_service_schema({vol.Required(ATTR_STOCK): int})
SERVICE_DATE = "set_date"
SERVICE_DATE_SCHEMA = make_entity_service_schema(
    {vol.Required(ATTR_NEW_DATE): cv.string}
)
SERVICE_REPLACED = "replace_action"
SERVICE_REPLACED_SCHEMA = make_entity_service_schema({})

# Helpers
UNIQUE_ID_FORMAT = "{}"
ENTITY_ID_FORMAT = PLATFORM + ".{}"
DATA_UPDATED = "replacements_updated"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""

    # Instantiate device and add to the platform
    config = hass.data[DOMAIN][config_entry.entry_id]

    # Generate a unique ID for each entity
    for entry in config[DOMAIN]:
        entry[CONF_UNIQUE_ID] = generate_entity_id(
            UNIQUE_ID_FORMAT, entry[CONF_PREFIX] + entry[CONF_NAME], []
        )

    replacements = [Replacement(entry) for entry in config[DOMAIN]]

    async_add_entities(replacements)

    # Get the platform reference
    platform = entity_platform.async_get_current_platform()

    ## Register all platform services

    # Register the stock update service
    platform.async_register_entity_service(
        SERVICE_STOCK, SERVICE_STOCK_SCHEMA, "async_handle_renew_stock"
    )

    # Register the set date service
    platform.async_register_entity_service(
        SERVICE_DATE, SERVICE_DATE_SCHEMA, "async_handle_set_date"
    )

    # Register the replacement action service
    platform.async_register_entity_service(
        SERVICE_REPLACED, SERVICE_REPLACED_SCHEMA, "async_handle_replace_action"
    )


@dataclass
class ReplacementSensorExtraStoredData(SensorExtraStoredData):
    """Object to hold extra stored data."""

    stock: int
    next_date: datetime | None

    def as_dict(self) -> dict[str, Any]:
        """Return a dict representation of the replacement sensor data."""
        data = super().as_dict()

        data[ATTR_STOCK] = self.stock
        data[ATTR_DATE] = None
        if isinstance(self.next_date, (datetime)):
            data[ATTR_DATE] = self.next_date.isoformat()
        return data

    @classmethod
    def from_dict(
        cls, restored: dict[str, Any]
    ) -> ReplacementSensorExtraStoredData | None:
        """Initialize a stored sensor state from a dict."""
        # Read the default SensorExtraStoredData, i.e., the native_value and
        # native_unit_of_measurement
        extra = SensorExtraStoredData.from_dict(restored)
        if extra is None:
            return None

        # Read the rest of the parameters
        try:
            stock: int = int(restored[ATTR_STOCK])
            next_date: datetime | None = dt_util.parse_datetime(restored[ATTR_DATE])
        except KeyError:
            # restored is a dict, but does not have all values
            return None

        return cls(
            extra.native_value, extra.native_unit_of_measurement, stock, next_date
        )


class Replacement(RestoreSensor):
    """Representation of a replacement sensor."""

    def __init__(self, replacement: dict[str, str]) -> None:
        """Initialize the Replacement sensor."""

        # Save all fields to identify the sensor
        self._unique_id = replacement[CONF_UNIQUE_ID]
        self.entity_id = ENTITY_ID_FORMAT.format(self._unique_id)
        self._name = replacement[CONF_NAME]

        ## Initialize all parameters that might be in the configuration

        # Get required configuration, one of these two must be defined
        #  according to the schema
        if CONF_DAYS_INTERVAL in replacement:
            self._days_interval = replacement[CONF_DAYS_INTERVAL]
            self._days_mode = True
        else:
            self._weeks_interval = replacement[CONF_WEEKS_INTERVAL]
            self._days_mode = False

        # Get additional optional parameters
        self._soon = replacement[CONF_SOON]
        self._unit_of_measurement = replacement[CONF_UNIT_OF_MEASUREMENT]
        self._icon_normal = replacement[CONF_ICON_NORMAL]
        self._icon_soon = replacement[CONF_ICON_SOON]
        self._icon_today = replacement[CONF_ICON_TODAY]
        self._icon_expired = replacement[CONF_ICON_EXPIRED]

        # Initialize the icon variable to the normal icon
        self._icon = self._icon_normal

        ## Initialize state and attributes

        # This initialization is usually replaced during state restore
        self._days_remaining = 0
        self._date = None
        self._stock = 0

    def _calculate_new_date(self):
        """Calculate a new replacement date according to the defined interval"""

        # Calculate the new date according to the interval
        if self._days_mode:
            next_date = date.today() + relativedelta(days=self._days_interval)
        else:
            next_date = date.today() + relativedelta(weeks=self._weeks_interval)

        # Replace new date with datetime
        self._date = datetime(next_date.year, next_date.month, next_date.day)

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        # Recover last sensor data
        restored = await self.async_get_last_sensor_data()

        if restored is None or restored.next_date is None:
            # We need to ensure a new date is calculated if the restored
            #  data is non-existent or corrupted
            self._calculate_new_date()
            return

        # Restore all saved attributes
        self._days_remaining = restored.native_value
        self._unit_of_measurement = restored.native_unit_of_measurement
        self._stock = restored.stock
        self._date = restored.next_date

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._days_remaining

    @property
    def native_unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit_of_measurement

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        res = {}

        # Return the interval according to the mode
        if self._days_mode:
            res[ATTR_DAYS_INTERVAL] = self._days_interval
        else:
            res[ATTR_WEEKS_INTERVAL] = self._weeks_interval

        # Return all other attributes
        res[ATTR_DATE] = self._date.strftime("%Y-%m-%d")
        res[ATTR_STOCK] = self._stock
        return res

    @property
    def icon(self):
        return self._icon

    @property
    def extra_restore_state_data(self) -> ReplacementSensorExtraStoredData:
        """Return sensor specific state data to be restored."""
        return ReplacementSensorExtraStoredData(
            self.native_value, self.native_unit_of_measurement, self._stock, self._date
        )

    async def async_get_last_sensor_data(
        self,
    ) -> ReplacementSensorExtraStoredData | None:
        """Restore Replacement Sensor Extra Stored Data."""
        if (restored_last_extra_data := await self.async_get_last_extra_data()) is None:
            return None

        return ReplacementSensorExtraStoredData.from_dict(
            restored_last_extra_data.as_dict()
        )

    async def async_handle_renew_stock(self, stock=-1) -> None:
        """Assign the new available stock"""
        self._stock = stock
        await self.async_update_ha_state()

    async def async_handle_set_date(self, new_date=None) -> None:
        """Assign a new date to replace"""

        # Verify the date is in the correct format
        try:
            try_date = datetime.strptime(new_date, "%Y-%m-%d")
        except ValueError as wrong_date_format:
            _LOGGER.warning('Invalid date, please input a date in format "YYYY-MM-DD"')
            raise AttributeError from wrong_date_format

        # Make sure the new date is not in the past
        if (try_date.date() - date.today()).days < 0:
            _LOGGER.warning("Invalid date, please input a date that is not in the past")
            raise ValueError

        # Assign the new date and update the state
        self._date = try_date
        await self.async_update_ha_state()

    async def async_handle_replace_action(self) -> None:
        """Handle what happens when a replacement occurs"""

        # Calculate new date from today
        self._calculate_new_date()

        # Decrement the stock
        if self._stock > 0:
            self._stock = self._stock - 1

        # Update the core state
        await self.async_update_ha_state()

    async def async_update(self) -> None:
        """update the sensor"""
        # Get today's date and calculate remaining days
        today = date.today()
        days_remaining = (self._date.date() - today).days

        # Assign icon according to number of days remaining
        if days_remaining < 0:
            self._icon = self._icon_expired
        elif days_remaining == 0:
            self._icon = self._icon_today
        elif days_remaining <= self._soon:
            self._icon = self._icon_soon
        else:
            self._icon = self._icon_normal

        # Update internal state
        self._days_remaining = days_remaining
