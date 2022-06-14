"""Tests for the config flow."""
from unittest import mock

import pytest

from custom_components.replacements import config_flow
from homeassistant import config_entries  # , data_entry_flow

from .const import MOCK_CONFIG_DAYS_ANOTHER  # , MOCK_CONFIG_WEEKS

from custom_components.replacements.const import (  # CONF_PREFIX,; CONF_UNIT_OF_MEASUREMENT,; CONF_ICON_EXPIRED,; CONF_ICON_NORMAL,; CONF_ICON_SOON,; CONF_ICON_TODAY,; CONF_ADD_ANOTHER,; DEFAULT_SOON,; DEFAULT_PREFIX,; DEFAULT_UNIT_OF_MEASUREMENT,; DEFAULT_ICON_NORMAL,; DEFAULT_ICON_SOON,; DEFAULT_ICON_TODAY,; DEFAULT_ICON_EXPIRED, COMPONENT_NAME,
    CONF_DAYS_INTERVAL,
    CONF_SOON,
    CONF_WEEKS_INTERVAL,
    DOMAIN,
)


# from homeassistant.const import CONF_NAME
# from pytest_homeassistant_custom_component.common import MockConfigEntry, patch


async def test_config_flow(hass):
    """Test the initialization of the form in the config flow."""

    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    expected = {
        "data_schema": config_flow.DATA_SCHEMA,
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
    _result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # test_input = []
    # test_input = MOCK_CONFIG_DAYS_ANOTHER
    # test_input[DOMAIN] = []
    # test_input[DOMAIN].append(MOCK_CONFIG_DAYS_ANOTHER)

    result = await hass.config_entries.flow.async_configure(
        _result["flow_id"],
        user_input=MOCK_CONFIG_DAYS_ANOTHER,
    )

    expected = {
        "data_schema": config_flow.DATA_SCHEMA,
        "description_placeholders": None,
        "errors": {},
        "flow_id": mock.ANY,
        "handler": DOMAIN,
        "step_id": "user",
        "type": "form",
        "last_step": None,
    }
    assert expected == result


# async def test_flow_user_creates_config_entry(hass):
#     """Test the config entry is successfully created."""
#     result = await hass.config_entries.flow.async_init(
#         config_flow.DOMAIN, context={"source": config_entries.SOURCE_USER}
#     )

#     result = await hass.config_entries.flow.async_configure(
#         result["flow_id"],
#         user_input=MOCK_CONFIG_WEEKS,
#     )


# expected = {
#     "version": 1,
#     "type": "create_entry",
#     "flow_id": mock.ANY,
#     "handler": DOMAIN,
#     "title": COMPONENT_NAME,
#     # "data": {
#     #     "access_token": "token",
#     #     "repositories": [
#     #         {"path": "home-assistant/core", "name": "home-assistant/core"}
#     #     ],
#     # },
#     "data": mock.ANY,
#     "description": None,
#     "description_placeholders": None,
#     "result": mock.ANY,
# }
# assert expected == result

# # If a user were to enter `test_username` for username and `test_password`
# # for password, it would result in this function call
# # for config in MOCK_CONFIG:
# result = await hass.config_entries.flow.async_configure(
#     result["flow_id"], user_input=MOCK_CONFIG
# )

# # Check that the config flow is complete and a new entry is created with
# # the input data
# assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
# assert result["title"] == COMPONENT_NAME
# assert result["data"] == MOCK_CONFIG
# assert result["result"]


# @patch("custom_components.github_custom.config_flow.validate_auth")
# async def test_flow_user_init_invalid_auth_token(m_validate_auth, hass):
#     """Test errors populated when auth token is invalid."""
#     m_validate_auth.side_effect = ValueError
#     _result = await hass.config_entries.flow.async_init(
#         config_flow.DOMAIN, context={"source": "user"}
#     )
#     result = await hass.config_entries.flow.async_configure(
#         _result["flow_id"], user_input={CONF_ACCESS_TOKEN: "bad"}
#     )
#     assert {"base": "auth"} == result["errors"]


# @patch("custom_components.github_custom.config_flow.validate_auth")
# async def test_flow_user_init_data_valid(m_validate_auth, hass):
#     """Test we advance to the next step when data is valid."""
#     _result = await hass.config_entries.flow.async_init(
#         config_flow.DOMAIN, context={"source": "user"}
#     )
#     result = await hass.config_entries.flow.async_configure(
#         _result["flow_id"], user_input={CONF_ACCESS_TOKEN: "bad"}
#     )
#     assert "repo" == result["step_id"]
#     assert "form" == result["type"]


# async def test_flow_repo_init_form(hass):
#     """Test the initialization of the form in the second step of the config flow."""
#     result = await hass.config_entries.flow.async_init(
#         config_flow.DOMAIN, context={"source": "repo"}
#     )
#     expected = {
#         "data_schema": config_flow.REPO_SCHEMA,
#         "description_placeholders": None,
#         "errors": {},
#         "flow_id": mock.ANY,
#         "handler": "github_custom",
#         "step_id": "repo",
#         "type": "form",
#     }
#     assert expected == result


# async def test_flow_repo_path_invalid(hass):
#     """Test errors populated when path is invalid."""
#     _result = await hass.config_entries.flow.async_init(
#         config_flow.DOMAIN, context={"source": "repo"}
#     )
#     result = await hass.config_entries.flow.async_configure(
#         _result["flow_id"], user_input={CONF_NAME: "bad", CONF_PATH: "bad"}
#     )
#     assert {"base": "invalid_path"} == result["errors"]


# async def test_flow_repo_add_another(hass):
#     """Test we show the repo flow again if the add_another box was checked."""
#     config_flow.GithubCustomConfigFlow.data = {
#         CONF_ACCESS_TOKEN: "token",
#         CONF_REPOS: [],
#     }
#     _result = await hass.config_entries.flow.async_init(
#         config_flow.DOMAIN, context={"source": "repo"}
#     )
#     result = await hass.config_entries.flow.async_configure(
#         _result["flow_id"],
#         user_input={CONF_PATH: "home-assistant/core", "add_another": True},
#     )
#     print(result)
#     assert "repo" == result["step_id"]
#     assert "form" == result["type"]


# async def test_flow_repo_creates_config_entry(hass):
#     """Test the config entry is successfully created."""
#     config_flow.GithubCustomConfigFlow.data = {
#         CONF_ACCESS_TOKEN: "token",
#         CONF_REPOS: [],
#     }
#     _result = await hass.config_entries.flow.async_init(
#         config_flow.DOMAIN, context={"source": "repo"}
#     )
#     result = await hass.config_entries.flow.async_configure(
#         _result["flow_id"],
#         user_input={CONF_PATH: "home-assistant/core"},
#     )
#     expected = {
#         "version": 1,
#         "type": "create_entry",
#         "flow_id": mock.ANY,
#         "handler": "github_custom",
#         "title": "GitHub Custom",
#         "data": {
#             "access_token": "token",
#             "repositories": [
#                 {"path": "home-assistant/core", "name": "home-assistant/core"}
#             ],
#         },
#         "description": None,
#         "description_placeholders": None,
#         "result": mock.ANY,
#     }
#     assert expected == result
