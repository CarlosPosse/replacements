"""Test Replacmeents setup process."""
from __future__ import annotations

from datetime import date, datetime

# Import everything provided by home assistant and the test component
from homeassistant.const import ATTR_DATE, CONF_NAME, CONF_PLATFORM
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.setup import async_setup_component
import homeassistant.util.dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

# Import everything from the integration
from custom_components.replacements.const import (
    COMPONENT_NAME,
    CONF_DAYS_INTERVAL,
    CONF_PREFIX,
    DOMAIN,
)
import custom_components.replacements.sensor as rp_sensor
from custom_components.replacements.sensor import ENTITY_ID_FORMAT, UNIQUE_ID_FORMAT

# Import everything from the tests
from .const import MOCK_CONFIG_DAYS, MOCK_CONFIG_WEEKS, MOCK_YAML_DAYS


async def test_restore_state(hass):
    """Test Replacements restore state."""

    # ID for the entity
    test_id = generate_entity_id(UNIQUE_ID_FORMAT, MOCK_YAML_DAYS[CONF_NAME], [])
    entity_id = ENTITY_ID_FORMAT.format(test_id)

    # Create mock configuration.yaml entry
    config = {DOMAIN: {test_id: MOCK_YAML_DAYS}}

    # Setup the entity
    assert await async_setup_component(hass, DOMAIN, config)
    await hass.async_block_till_done()

    # Restore state from cache
    state = hass.states.get(entity_id)

    # Get the calculated date from the new entity
    new_date: datetime | None = dt_util.parse_datetime(state.attributes[ATTR_DATE])

    # Check that the new date is correct. This must be equal to the configured interval
    today = date.today()
    days_remaining = (new_date.date() - today).days

    assert days_remaining == MOCK_YAML_DAYS[CONF_DAYS_INTERVAL]


async def test_setup_missing_discovery(hass):
    """Test setup with configuration missing discovery_info."""
    assert not await rp_sensor.async_setup_platform(hass, {CONF_PLATFORM: DOMAIN}, None)
    assert not await rp_sensor.async_setup_platform(hass, {CONF_PLATFORM: DOMAIN}, None)


async def test_setup_and_remove_config_entry_single_entity(hass) -> None:
    """Test setting up and removing a config entry."""
    registry = er.async_get(hass)

    # Generate the entities in the entry
    test_data = {}
    test_data[DOMAIN] = []
    test_data[DOMAIN].append(MOCK_CONFIG_DAYS)

    # Generate all the entity IDs
    expected_entities = []
    for entry in test_data[DOMAIN]:
        expected_entities.append(
            generate_entity_id(
                ENTITY_ID_FORMAT, entry[CONF_PREFIX] + entry[CONF_NAME], []
            )
        )

    # Setup the config entry
    config_entry = MockConfigEntry(domain=DOMAIN, title=COMPONENT_NAME, data=test_data)
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_all()) == len(test_data[DOMAIN])
    assert len(registry.entities) == len(test_data[DOMAIN])
    for entity in expected_entities:
        assert hass.states.get(entity)
        assert entity in registry.entities

    # Reload the entry and assert that the data from above is still there
    assert await hass.config_entries.async_reload(config_entry.entry_id)
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]

    # Remove the config entry
    assert await hass.config_entries.async_remove(config_entry.entry_id)
    await hass.async_block_till_done()

    # Check the state and entity registry entry are removed
    assert len(hass.states.async_all()) == 0
    assert len(registry.entities) == 0


async def test_setup_and_remove_config_entry_multiple_entities(hass) -> None:
    """Test setting up and removing a config entry."""
    registry = er.async_get(hass)

    # Generate the entities in the entry
    test_data = {}
    test_data[DOMAIN] = []
    test_data[DOMAIN].append(MOCK_CONFIG_DAYS)
    test_data[DOMAIN].append(MOCK_CONFIG_WEEKS)

    # Generate all the entity IDs
    expected_entities = []
    for entry in test_data[DOMAIN]:
        expected_entities.append(
            generate_entity_id(
                ENTITY_ID_FORMAT, entry[CONF_PREFIX] + entry[CONF_NAME], []
            )
        )

    # Setup the config entry
    config_entry = MockConfigEntry(domain=DOMAIN, title=COMPONENT_NAME, data=test_data)
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_all()) == len(test_data[DOMAIN])
    assert len(registry.entities) == len(test_data[DOMAIN])
    for entity in expected_entities:
        assert hass.states.get(entity)
        assert entity in registry.entities

    # Reload the entry and assert that the data from above is still there
    assert await hass.config_entries.async_reload(config_entry.entry_id)
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]

    # Remove the config entry
    assert await hass.config_entries.async_remove(config_entry.entry_id)
    await hass.async_block_till_done()

    # Check the state and entity registry entry are removed
    assert len(hass.states.async_all()) == 0
    assert len(registry.entities) == 0
