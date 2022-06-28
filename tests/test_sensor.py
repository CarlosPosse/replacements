"""Tests for the sensor module."""
from __future__ import annotations

from datetime import date, datetime, timedelta

# Import everything provided by home assistant and the test component
from homeassistant.const import (
    ATTR_DATE,
    ATTR_ENTITY_ID,
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_NAME,
    CONF_UNIT_OF_MEASUREMENT,
    EVENT_HOMEASSISTANT_START,
)
from homeassistant.core import State
from homeassistant.helpers.entity import generate_entity_id
import homeassistant.util.dt as dt_util
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
    mock_restore_cache_with_extra_data,
    patch,
)

# Import everything from the integration
from custom_components.replacements.const import (
    COMPONENT_NAME,
    CONF_DAYS_INTERVAL,
    CONF_PREFIX,
    CONF_WEEKS_INTERVAL,
    DOMAIN,
)
from custom_components.replacements.sensor import (
    ATTR_DAYS_INTERVAL,
    ATTR_NEW_DATE,
    ATTR_STOCK,
    ATTR_WEEKS_INTERVAL,
    ENTITY_ID_FORMAT,
    SERVICE_DATE,
    SERVICE_REPLACED,
    SERVICE_STOCK,
    UNIQUE_ID_FORMAT,
)

# Import everything from the tests
from .const import MOCK_CONFIG_DAYS, MOCK_CONFIG_WEEKS

# from .mock_datetime import mock_datetime


def calculate_days_remaining(hass, entity_id) -> int:
    """Get the number of days remaining for a specific entity."""
    # Restore state from cache
    state = hass.states.get(entity_id)

    # Get the calculated date from the new entity
    new_date: datetime | None = dt_util.parse_datetime(state.attributes[ATTR_DATE])

    # Check that the new date is correct. This must be equal to the configured interval
    today = date.today()
    return (new_date.date() - today).days


@pytest.fixture(autouse=True)
def set_utc(hass):
    """Set timezone to UTC."""
    hass.config.set_time_zone("UTC")


async def test_state(hass):
    """Test replacement sensor state."""

    # Test entities
    yaml_store_mock = MOCK_CONFIG_DAYS
    yaml_normal_mock = MOCK_CONFIG_WEEKS

    # Definitions for state restore test
    test_store_native_value = 6
    test_store_days = 5
    test_store_date = date.today() + timedelta(days=test_store_days)
    test_store_stock = 5

    # Definitions for state update test
    test_elapse_days = 3
    test_elapsed_date = date.today() + timedelta(days=test_elapse_days)

    # Generate IDs for the entities

    test_data = {}
    test_data[DOMAIN] = []
    test_data[DOMAIN].append(yaml_store_mock)
    test_data[DOMAIN].append(yaml_normal_mock)

    # Generate all the entity IDs
    expected_entities = []
    for entry in test_data[DOMAIN]:
        expected_entities.append(
            generate_entity_id(
                ENTITY_ID_FORMAT, entry[CONF_PREFIX] + entry[CONF_NAME], []
            )
        )

    yaml_store_unique_id = generate_entity_id(
        UNIQUE_ID_FORMAT, yaml_store_mock[CONF_PREFIX] + yaml_store_mock[CONF_NAME], []
    )
    yaml_store_entity_id = ENTITY_ID_FORMAT.format(yaml_store_unique_id)

    yaml_normal_unique_id = generate_entity_id(
        UNIQUE_ID_FORMAT,
        yaml_normal_mock[CONF_PREFIX] + yaml_normal_mock[CONF_NAME],
        [],
    )
    yaml_normal_entity_id = ENTITY_ID_FORMAT.format(yaml_normal_unique_id)

    # Setup the restore cache for just the yaml_store_entity
    # Note: we purposefully store a wrong native value, which will
    #  be correct on the next update
    mock_restore_cache_with_extra_data(
        hass,
        [
            (
                State(
                    yaml_store_entity_id,
                    0,
                    attributes={},
                ),
                {
                    "native_value": {
                        "__type": "<class 'decimal.Decimal'>",
                        "decimal_str": test_store_native_value,
                    },
                    "native_unit_of_measurement": yaml_store_mock[
                        CONF_UNIT_OF_MEASUREMENT
                    ],
                    ATTR_DAYS_INTERVAL: yaml_store_mock[CONF_DAYS_INTERVAL],
                    ATTR_DATE: test_store_date.isoformat(),
                    ATTR_STOCK: test_store_stock,
                },
            )
        ],
    )

    # Setup the config entry
    config_entry = MockConfigEntry(domain=DOMAIN, title=COMPONENT_NAME, data=test_data)
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Start the home assistant instance
    hass.bus.async_fire(EVENT_HOMEASSISTANT_START)
    await hass.async_block_till_done()

    # Assert that all properties are as expected for the normal entity
    expected_normal_date = date.today() + timedelta(
        weeks=yaml_normal_mock[CONF_WEEKS_INTERVAL]
    )
    state = hass.states.get(yaml_normal_entity_id)

    assert int(state.state) == 0
    assert (
        state.attributes[ATTR_WEEKS_INTERVAL] == yaml_normal_mock[CONF_WEEKS_INTERVAL]
    )
    assert state.attributes[ATTR_DATE] == expected_normal_date.isoformat()
    assert state.attributes[ATTR_STOCK] == 0
    assert (
        state.attributes[ATTR_UNIT_OF_MEASUREMENT]
        == yaml_normal_mock[CONF_UNIT_OF_MEASUREMENT]
    )

    # Assert that all properties are as expected for the restored entity
    state = hass.states.get(yaml_store_entity_id)
    assert int(state.state) == test_store_native_value
    assert state.attributes[ATTR_DAYS_INTERVAL] == yaml_store_mock[CONF_DAYS_INTERVAL]
    assert state.attributes[ATTR_DATE] == test_store_date.isoformat()
    assert state.attributes[ATTR_STOCK] == test_store_stock
    assert (
        state.attributes[ATTR_UNIT_OF_MEASUREMENT]
        == yaml_store_mock[CONF_UNIT_OF_MEASUREMENT]
    )

    # Force refresh of the configured entities, simulating some days have passed
    now = dt_util.utcnow() + timedelta(days=test_elapse_days)

    with patch("tests.test_sensor.date") as mock_test_date, patch(
        "custom_components.replacements.sensor.date"
    ) as mock_sensor_date, patch("homeassistant.util.dt.utcnow", return_value=now):
        mock_test_date.today.return_value = test_elapsed_date
        mock_sensor_date.today.return_value = test_elapsed_date

        async_fire_time_changed(hass, now)
        await hass.async_block_till_done()

        # Assert that all properties are as expected for the normal entity
        state = hass.states.get(yaml_normal_entity_id)

        assert int(state.state) == (expected_normal_date - now.date()).days
        assert (
            state.attributes[ATTR_WEEKS_INTERVAL]
            == yaml_normal_mock[CONF_WEEKS_INTERVAL]
        )
        assert state.attributes[ATTR_DATE] == expected_normal_date.isoformat()
        assert state.attributes[ATTR_STOCK] == 0
        assert (
            state.attributes[ATTR_UNIT_OF_MEASUREMENT]
            == yaml_normal_mock[CONF_UNIT_OF_MEASUREMENT]
        )

        # Assert that all properties are as expected for the restored entity
        state = hass.states.get(yaml_store_entity_id)
        assert int(state.state) == calculate_days_remaining(hass, yaml_store_entity_id)
        assert (
            state.attributes[ATTR_DAYS_INTERVAL] == yaml_store_mock[CONF_DAYS_INTERVAL]
        )
        assert state.attributes[ATTR_DATE] == test_store_date.isoformat()
        assert state.attributes[ATTR_STOCK] == test_store_stock
        assert (
            state.attributes[ATTR_UNIT_OF_MEASUREMENT]
            == yaml_store_mock[CONF_UNIT_OF_MEASUREMENT]
        )


async def test_no_stored_extra_data(hass):
    """Test replacement sensor state."""

    # Test entities
    yaml_mock = MOCK_CONFIG_DAYS

    test_data = {}
    test_data[DOMAIN] = []
    test_data[DOMAIN].append(yaml_mock)

    # Definitions for state restore test
    test_days = 5
    test_date = date.today() + timedelta(days=test_days)
    test_stock = 5

    # Generate IDs for the entities
    yaml_unique_id = generate_entity_id(
        UNIQUE_ID_FORMAT, yaml_mock[CONF_PREFIX] + yaml_mock[CONF_NAME], []
    )
    yaml_entity_id = ENTITY_ID_FORMAT.format(yaml_unique_id)

    # Setup the restore cache for just the yaml_store_entity
    # Note: We purposefully omit the native_value and native_unit of measurement
    # fields to force a fail in the extra data restore
    mock_restore_cache_with_extra_data(
        hass,
        [
            (
                State(
                    yaml_entity_id,
                    0,
                    attributes={},
                ),
                {
                    # "native_value": {
                    #     "__type": "<class 'decimal.Decimal'>",
                    #     "decimal_str": test_store_native_value,
                    # },
                    # "native_unit_of_measurement": yaml_mock[
                    #     CONF_UNIT_OF_MEASUREMENT
                    # ],
                    ATTR_DAYS_INTERVAL: yaml_mock[CONF_DAYS_INTERVAL],
                    ATTR_DATE: test_date.isoformat(),
                    ATTR_STOCK: test_stock,
                },
            )
        ],
    )

    # Setup the config entry
    config_entry = MockConfigEntry(domain=DOMAIN, title=COMPONENT_NAME, data=test_data)
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Start the home assistant instance
    hass.bus.async_fire(EVENT_HOMEASSISTANT_START)
    await hass.async_block_till_done()

    # Assert that all properties are as expected for the restored entity
    expected_date = date.today() + timedelta(days=yaml_mock[CONF_DAYS_INTERVAL])
    state = hass.states.get(yaml_entity_id)

    assert int(state.state) == 0
    assert state.attributes[ATTR_DAYS_INTERVAL] == yaml_mock[CONF_DAYS_INTERVAL]
    assert state.attributes[ATTR_DATE] == expected_date.isoformat()
    assert state.attributes[ATTR_STOCK] == 0
    assert (
        state.attributes[ATTR_UNIT_OF_MEASUREMENT]
        == yaml_mock[CONF_UNIT_OF_MEASUREMENT]
    )


async def test_no_stored_stock(hass):
    """Test replacement sensor state."""

    # Test entities
    yaml_mock = MOCK_CONFIG_DAYS

    test_data = {}
    test_data[DOMAIN] = []
    test_data[DOMAIN].append(yaml_mock)

    # Definitions for state restore test
    test_native_value = 10
    test_days = 5
    test_date = date.today() + timedelta(days=test_days)

    # Generate IDs for the entities
    yaml_unique_id = generate_entity_id(
        UNIQUE_ID_FORMAT, yaml_mock[CONF_PREFIX] + yaml_mock[CONF_NAME], []
    )
    yaml_entity_id = ENTITY_ID_FORMAT.format(yaml_unique_id)

    # Setup the restore cache for just the yaml_store_entity
    # Note: We purposefully omit the stock to force a key error
    mock_restore_cache_with_extra_data(
        hass,
        [
            (
                State(
                    yaml_entity_id,
                    0,
                    attributes={},
                ),
                {
                    "native_value": {
                        "__type": "<class 'decimal.Decimal'>",
                        "decimal_str": test_native_value,
                    },
                    "native_unit_of_measurement": yaml_mock[CONF_UNIT_OF_MEASUREMENT],
                    ATTR_DAYS_INTERVAL: yaml_mock[CONF_DAYS_INTERVAL],
                    ATTR_DATE: test_date.isoformat(),
                    # ATTR_STOCK: 5,
                },
            )
        ],
    )

    # Setup the config entry
    config_entry = MockConfigEntry(domain=DOMAIN, title=COMPONENT_NAME, data=test_data)
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Start the home assistant instance
    hass.bus.async_fire(EVENT_HOMEASSISTANT_START)
    await hass.async_block_till_done()

    # Assert that all properties are as expected for the restored entity
    expected_date = date.today() + timedelta(days=yaml_mock[CONF_DAYS_INTERVAL])
    state = hass.states.get(yaml_entity_id)

    assert int(state.state) == 0
    assert state.attributes[ATTR_DAYS_INTERVAL] == yaml_mock[CONF_DAYS_INTERVAL]
    assert state.attributes[ATTR_DATE] == expected_date.isoformat()
    assert state.attributes[ATTR_STOCK] == 0
    assert (
        state.attributes[ATTR_UNIT_OF_MEASUREMENT]
        == yaml_mock[CONF_UNIT_OF_MEASUREMENT]
    )


async def test_no_stored_date(hass):
    """Test replacement sensor state."""

    # Test entities
    yaml_mock = MOCK_CONFIG_DAYS

    test_data = {}
    test_data[DOMAIN] = []
    test_data[DOMAIN].append(yaml_mock)

    # Definitions for state restore test
    test_native_value = 10
    test_stock = 10

    # Generate IDs for the entities
    yaml_unique_id = generate_entity_id(
        UNIQUE_ID_FORMAT, yaml_mock[CONF_PREFIX] + yaml_mock[CONF_NAME], []
    )
    yaml_entity_id = ENTITY_ID_FORMAT.format(yaml_unique_id)

    # Setup the restore cache for just the yaml_store_entity
    # Note: We purposefully omit the date to force a key error
    mock_restore_cache_with_extra_data(
        hass,
        [
            (
                State(
                    yaml_entity_id,
                    0,
                    attributes={},
                ),
                {
                    "native_value": {
                        "__type": "<class 'decimal.Decimal'>",
                        "decimal_str": test_native_value,
                    },
                    "native_unit_of_measurement": yaml_mock[CONF_UNIT_OF_MEASUREMENT],
                    ATTR_DAYS_INTERVAL: yaml_mock[CONF_DAYS_INTERVAL],
                    # ATTR_DATE: "213jkbdsg",
                    ATTR_STOCK: test_stock,
                },
            )
        ],
    )

    # Setup the config entry
    config_entry = MockConfigEntry(domain=DOMAIN, title=COMPONENT_NAME, data=test_data)
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Start the home assistant instance
    hass.bus.async_fire(EVENT_HOMEASSISTANT_START)
    await hass.async_block_till_done()

    # Assert that all properties are as expected for the restored entity
    expected_date = date.today() + timedelta(days=yaml_mock[CONF_DAYS_INTERVAL])
    state = hass.states.get(yaml_entity_id)

    assert int(state.state) == 0
    assert state.attributes[ATTR_DAYS_INTERVAL] == yaml_mock[CONF_DAYS_INTERVAL]
    assert state.attributes[ATTR_DATE] == expected_date.isoformat()
    assert state.attributes[ATTR_STOCK] == 0
    assert (
        state.attributes[ATTR_UNIT_OF_MEASUREMENT]
        == yaml_mock[CONF_UNIT_OF_MEASUREMENT]
    )


async def test_wrong_stored_date(hass):
    """Test replacement sensor state."""

    # Test entities
    yaml_mock = MOCK_CONFIG_DAYS

    test_data = {}
    test_data[DOMAIN] = []
    test_data[DOMAIN].append(yaml_mock)

    # Definitions for state restore test
    test_native_value = 10
    test_stock = 10

    # Generate IDs for the entities
    yaml_unique_id = generate_entity_id(
        UNIQUE_ID_FORMAT, yaml_mock[CONF_PREFIX] + yaml_mock[CONF_NAME], []
    )
    yaml_entity_id = ENTITY_ID_FORMAT.format(yaml_unique_id)

    # Setup the restore cache for just the yaml_store_entity
    # Note: We purposefully give a wrong date to force an invalid operation
    mock_restore_cache_with_extra_data(
        hass,
        [
            (
                State(
                    yaml_entity_id,
                    0,
                    attributes={},
                ),
                {
                    "native_value": {
                        "__type": "<class 'decimal.Decimal'>",
                        "decimal_str": test_native_value,
                    },
                    "native_unit_of_measurement": yaml_mock[CONF_UNIT_OF_MEASUREMENT],
                    ATTR_DAYS_INTERVAL: yaml_mock[CONF_DAYS_INTERVAL],
                    ATTR_DATE: "213jkbdsg",
                    ATTR_STOCK: test_stock,
                },
            )
        ],
    )

    # Setup the config entry
    config_entry = MockConfigEntry(domain=DOMAIN, title=COMPONENT_NAME, data=test_data)
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Start the home assistant instance
    hass.bus.async_fire(EVENT_HOMEASSISTANT_START)
    await hass.async_block_till_done()

    # Assert that all properties are as expected for the restored entity
    expected_date = date.today() + timedelta(days=yaml_mock[CONF_DAYS_INTERVAL])
    state = hass.states.get(yaml_entity_id)

    assert int(state.state) == 0
    assert state.attributes[ATTR_DAYS_INTERVAL] == yaml_mock[CONF_DAYS_INTERVAL]
    assert state.attributes[ATTR_DATE] == expected_date.isoformat()
    assert state.attributes[ATTR_STOCK] == 0
    assert (
        state.attributes[ATTR_UNIT_OF_MEASUREMENT]
        == yaml_mock[CONF_UNIT_OF_MEASUREMENT]
    )


async def test_services(hass):
    """Test replacement sensor services with a config entry."""
    entry_mock = MOCK_CONFIG_DAYS
    test_elapse_days = 3
    test_date = date.today() + timedelta(days=test_elapse_days)
    test_stock = 10

    # Generate the entities in the entry
    test_data = {}
    test_data[DOMAIN] = []
    test_data[DOMAIN].append(entry_mock)

    entry_entity_id = generate_entity_id(
        ENTITY_ID_FORMAT, entry_mock[CONF_PREFIX] + entry_mock[CONF_NAME], []
    )

    # Add the config entry
    config_entry = MockConfigEntry(domain=DOMAIN, title=COMPONENT_NAME, data=test_data)
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Start the home assistant instance
    hass.bus.async_fire(EVENT_HOMEASSISTANT_START)
    await hass.async_block_till_done()

    # Test the replace service when the entity has no stock
    state = hass.states.get(entry_entity_id)
    assert state.attributes[ATTR_STOCK] == 0

    await hass.services.async_call(
        DOMAIN,
        SERVICE_REPLACED,
        {ATTR_ENTITY_ID: entry_entity_id},
        blocking=True,
    )
    state = hass.states.get(entry_entity_id)
    assert state.attributes[ATTR_STOCK] == 0

    # Test the stock service
    await hass.services.async_call(
        DOMAIN,
        SERVICE_STOCK,
        {ATTR_ENTITY_ID: entry_entity_id, ATTR_STOCK: test_stock},
        blocking=True,
    )
    state = hass.states.get(entry_entity_id)
    assert state.attributes[ATTR_STOCK] == test_stock

    # Test the replace service
    await hass.services.async_call(
        DOMAIN,
        SERVICE_REPLACED,
        {ATTR_ENTITY_ID: entry_entity_id},
        blocking=True,
    )
    state = hass.states.get(entry_entity_id)
    assert state.attributes[ATTR_STOCK] == test_stock - 1

    # Test the new date service
    await hass.services.async_call(
        DOMAIN,
        SERVICE_DATE,
        {ATTR_ENTITY_ID: entry_entity_id, ATTR_NEW_DATE: test_date.isoformat()},
        blocking=True,
    )
    assert calculate_days_remaining(hass, entry_entity_id) == test_elapse_days

    # Test wrong date format on the date service
    with pytest.raises(AttributeError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_DATE,
            {ATTR_ENTITY_ID: entry_entity_id, ATTR_NEW_DATE: "25-05"},
            blocking=True,
        )

    # Test a date that has already passed on the date service
    with pytest.raises(ValueError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_DATE,
            {ATTR_ENTITY_ID: entry_entity_id, ATTR_NEW_DATE: "1991-04-26"},
            blocking=True,
        )
