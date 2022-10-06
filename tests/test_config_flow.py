"""Tests for the config flow."""
from unittest import mock

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry, patch

from custom_components.replacements import config_flow
from custom_components.replacements.const import (
    COMPONENT_NAME,
    CONF_DAYS_INTERVAL,
    CONF_PREFIX,
    CONF_SOON,
    CONF_WEEKS_INTERVAL,
    DOMAIN,
)
from custom_components.replacements.sensor import ENTITY_ID_FORMAT
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers.entity import generate_entity_id

from .const import (
    MOCK_CONFIG_ADDITIONAL,
    MOCK_CONFIG_DAYS,
    MOCK_CONFIG_ERROR,
    MOCK_CONFIG_SMALL,
    MOCK_CONFIG_WEEKS,
)


async def test_config_flow(hass):
    """Test the initialization of the form in the config flow."""

    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    expected = {
        "data_schema": config_flow.ENTRY_SCHEMA,
        "description_placeholders": None,
        "errors": {},
        "flow_id": mock.ANY,
        "handler": DOMAIN,
        "step_id": "user",
        "type": "form",
        "last_step": None,
    }
    assert expected == result


def test_validate_soon_valid():
    """Test no exception is raised for a valid soon configuration."""
    test_input = []

    # Test valid days interval
    test_input.append(
        {
            CONF_DAYS_INTERVAL: 6,
            CONF_SOON: 3,
        }
    )

    # Test valid weeks interval
    test_input.append(
        {
            CONF_WEEKS_INTERVAL: 6,
            CONF_SOON: 4,
        }
    )

    for soon in test_input:
        config_flow.validate_soon(soon)


def test_validate_soon_invalid():
    """Test a ValueError is raised when the soon configuration is not valid."""
    test_input = []

    # Test valid days interval
    test_input.append(
        {
            CONF_DAYS_INTERVAL: 2,
            CONF_SOON: 3,
        }
    )

    # Test valid weeks interval
    test_input.append(
        {
            CONF_WEEKS_INTERVAL: 1,
            CONF_SOON: 4,
        }
    )

    for soon in test_input:
        with pytest.raises(ValueError):
            config_flow.validate_soon(soon)


async def test_flow_user_add_another(hass):
    """Test we show the user flow again if the add_another box was checked."""
    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=MOCK_CONFIG_DAYS,
    )

    expected = {
        "data_schema": config_flow.ENTRY_SCHEMA,
        "description_placeholders": None,
        "errors": {},
        "flow_id": mock.ANY,
        "handler": DOMAIN,
        "step_id": "user",
        "type": "form",
        "last_step": None,
    }
    assert expected == result


async def test_flow_user_creates_config_entry(hass):
    """Test the config entry is successfully created."""
    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # We patch the setup_entry function as we are just testing the config flow,
    #  not the actual setup itself
    with patch(
        "custom_components.replacements.async_setup_entry",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=MOCK_CONFIG_SMALL,
        )
        await hass.async_block_till_done()

    expected = {
        "version": 1,
        "type": "create_entry",
        "flow_id": mock.ANY,
        "handler": DOMAIN,
        "title": COMPONENT_NAME,
        "data": mock.ANY,
        "description": None,
        "description_placeholders": None,
        "options": {},
        "result": mock.ANY,
        "context": {"source": "user"},
    }
    assert expected == result


async def test_flow_user_creates_config_entry_multiple(hass):
    """Test the config entry is successfully created."""
    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    flow_id = result["flow_id"]

    # Configure multiple entities using the config flow
    result = await hass.config_entries.flow.async_configure(
        flow_id,
        user_input=MOCK_CONFIG_DAYS,
    )

    # We patch the setup_entry function as we are just testing the config flow,
    #  not the actual setup itself
    with patch(
        "custom_components.replacements.async_setup_entry",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_configure(
            flow_id,
            user_input=MOCK_CONFIG_WEEKS,
        )
        await hass.async_block_till_done()

    expected = {
        "version": 1,
        "type": "create_entry",
        "flow_id": mock.ANY,
        "handler": DOMAIN,
        "title": COMPONENT_NAME,
        "data": mock.ANY,
        "description": None,
        "description_placeholders": None,
        "options": {},
        "result": mock.ANY,
        "context": {"source": "user"},
    }
    assert expected == result


async def test_options_flow_init(hass):
    """Test config flow options."""
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

    # Generate a config entry
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="config_entry_test",
        data=test_data,
    )

    # Add the entry to home assistant
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Show initial options form
    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    # Test for correct form
    assert result["type"] == "form"
    assert result["step_id"] == "init"
    assert result["errors"] == {}

    # Test that the multi-select options has the configured replacements
    for entity in expected_entities:
        assert entity in result["data_schema"].schema[DOMAIN].options


async def test_options_flow_add_replacement(hass):
    """Test config flow options."""
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

    # Generate a config entry
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="config_entry_test",
        data=test_data,
    )

    # Add the entry to home assistant
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Show initial options form
    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    # Add a new entry
    add_data = {DOMAIN: expected_entities}
    add_data.update(MOCK_CONFIG_ADDITIONAL)

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input=add_data,
    )
    assert result["type"] == "create_entry"
    assert result["title"] == COMPONENT_NAME
    assert result["result"] is True
    assert result["data"] == {
        DOMAIN: [MOCK_CONFIG_ADDITIONAL, MOCK_CONFIG_DAYS, MOCK_CONFIG_WEEKS]
    }


async def test_options_flow_add_error_replacement(hass):
    """Test config flow options."""
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

    # Generate a config entry
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="config_entry_test",
        data=test_data,
    )

    # Add the entry to home assistant
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Show initial options form
    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    # Add a new entry
    add_data = {DOMAIN: expected_entities}
    add_data.update(MOCK_CONFIG_ERROR)

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input=add_data,
    )
    assert result["type"] == "form"
    assert result["step_id"] == "init"
    assert result["errors"] == {"base": "invalid_soon"}

    # # Test that the multi-select options has the configured replacements
    for entity in expected_entities:
        assert entity in result["data_schema"].schema[DOMAIN].options


async def test_options_flow_remove_replacement(hass):
    """Test config flow options."""
    test_data = {}
    test_data[DOMAIN] = []
    test_data[DOMAIN].append(MOCK_CONFIG_DAYS)
    test_data[DOMAIN].append(MOCK_CONFIG_WEEKS)

    # Generate all the entity IDs
    save_entity = generate_entity_id(
        ENTITY_ID_FORMAT,
        MOCK_CONFIG_DAYS[CONF_PREFIX] + MOCK_CONFIG_DAYS[CONF_NAME],
        [],
    )

    # Generate a config entry
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="config_entry_test",
        data=test_data,
    )

    # Add the entry to home assistant
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Show initial options form
    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    # Remove one of the entries
    remove_data = {DOMAIN: [save_entity]}

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input=remove_data,
    )
    assert result["type"] == "create_entry"
    assert result["title"] == COMPONENT_NAME
    assert result["result"] is True
    assert result["data"] == {DOMAIN: [MOCK_CONFIG_DAYS]}
