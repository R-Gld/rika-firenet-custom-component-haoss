"""Test Rika Firenet config flow."""
from unittest.mock import MagicMock, patch

import pytest
from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from custom_components.rika_firenet.const import CONF_DEFAULT_TEMPERATURE, DOMAIN
from custom_components.rika_firenet.exceptions import (
    RikaAuthenticationError,
    RikaConnectionError,
    RikaTimeoutError,
)


@pytest.fixture
def mock_setup_entry():
    """Mock successful setup entry."""
    with patch(
        "custom_components.rika_firenet.async_setup_entry", return_value=True
    ) as mock_setup:
        yield mock_setup


async def test_user_form(hass, mock_requests):
    """Test that the user form is served."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}


async def test_user_flow_success(hass, mock_requests, mock_setup_entry):
    """Test successful user flow."""
    with patch(
        "custom_components.rika_firenet.config_flow.RikaFirenetCoordinator"
    ) as mock_coordinator:
        # Mock successful setup
        coordinator_instance = MagicMock()
        coordinator_instance.setup = MagicMock()
        mock_coordinator.return_value = coordinator_instance

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "test@example.com",
                CONF_PASSWORD: "test_password",
            },
        )

        assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
        assert result["title"] == "test@example.com"
        assert result["data"] == {
            CONF_USERNAME: "test@example.com",
            CONF_PASSWORD: "test_password",
        }


async def test_user_flow_authentication_error(hass, mock_requests):
    """Test user flow with authentication error."""
    with patch(
        "custom_components.rika_firenet.config_flow.RikaFirenetCoordinator"
    ) as mock_coordinator:
        # Mock authentication failure
        coordinator_instance = MagicMock()
        coordinator_instance.setup.side_effect = RikaAuthenticationError(
            "Invalid credentials"
        )
        mock_coordinator.return_value = coordinator_instance

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "test@example.com",
                CONF_PASSWORD: "wrong_password",
            },
        )

        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["errors"] == {"base": "auth"}


async def test_user_flow_connection_error(hass, mock_requests):
    """Test user flow with connection error."""
    with patch(
        "custom_components.rika_firenet.config_flow.RikaFirenetCoordinator"
    ) as mock_coordinator:
        # Mock connection error
        coordinator_instance = MagicMock()
        coordinator_instance.setup.side_effect = RikaConnectionError("Connection failed")
        mock_coordinator.return_value = coordinator_instance

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "test@example.com",
                CONF_PASSWORD: "test_password",
            },
        )

        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["errors"] == {"base": "auth"}


async def test_user_flow_timeout_error(hass, mock_requests):
    """Test user flow with timeout error."""
    with patch(
        "custom_components.rika_firenet.config_flow.RikaFirenetCoordinator"
    ) as mock_coordinator:
        # Mock timeout error
        coordinator_instance = MagicMock()
        coordinator_instance.setup.side_effect = RikaTimeoutError("Connection timeout")
        mock_coordinator.return_value = coordinator_instance

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "test@example.com",
                CONF_PASSWORD: "test_password",
            },
        )

        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["errors"] == {"base": "auth"}


async def test_single_instance_allowed(hass, mock_requests, mock_setup_entry):
    """Test that only a single instance is allowed."""
    # Create first entry
    with patch(
        "custom_components.rika_firenet.config_flow.RikaFirenetCoordinator"
    ) as mock_coordinator:
        coordinator_instance = MagicMock()
        coordinator_instance.setup = MagicMock()
        mock_coordinator.return_value = coordinator_instance

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "test@example.com",
                CONF_PASSWORD: "test_password",
            },
        )

        assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY

    # Try to create second entry
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == data_entry_flow.FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"


async def test_options_flow(hass, mock_config_entry, mock_options):
    """Test options flow."""
    # Create a config entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=mock_config_entry,
        options=mock_options,
    )
    entry.add_to_hass(hass)

    # Initialize options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    # Update options
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_DEFAULT_TEMPERATURE: 22,
            "climate": True,
            "sensor": True,
            "switch": False,
            "number": True,
            "binary_sensor": True,
        },
    )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_DEFAULT_TEMPERATURE] == 22
    assert result["data"]["switch"] is False


# Helper class for mock config entry
class MockConfigEntry:
    """Mock config entry."""

    def __init__(self, domain, data, options=None):
        """Initialize mock config entry."""
        self.domain = domain
        self.data = data
        self.options = options or {}
        self.entry_id = "test_entry_id"

    def add_to_hass(self, hass):
        """Add to hass."""
        hass.config_entries._entries[self.entry_id] = self
