"""Common fixtures for Rika Firenet tests."""
import json
from unittest.mock import MagicMock, patch

import pytest
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from custom_components.rika_firenet.const import CONF_DEFAULT_TEMPERATURE, DOMAIN

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test dir."""
    yield


@pytest.fixture
def mock_config_entry():
    """Return a mock config entry."""
    return {
        CONF_USERNAME: "test@example.com",
        CONF_PASSWORD: "test_password",
    }


@pytest.fixture
def mock_options():
    """Return mock options."""
    return {
        CONF_DEFAULT_TEMPERATURE: 21,
        "climate": True,
        "sensor": True,
        "switch": True,
        "number": True,
        "binary_sensor": True,
    }


@pytest.fixture
def mock_stove_state():
    """Return a mock stove state response."""
    return {
        "sensors": {
            "parameterFeedRateTotal": 150.5,
            "parameterRuntimePellets": 2500,
            "inputFlameTemperature": 85.5,
            "inputRoomTemperature": 21.2,
            "statusMainState": 4,
            "statusSubState": 0,
            "statusFrostStarted": False,
        },
        "controls": {
            "targetTemperature": "22",
            "operatingMode": 0,
            "setBackTemperature": "18",
            "heatingTimesActiveForComfort": True,
            "onOff": True,
            "convectionFan1Active": True,
            "convectionFan1Level": 3,
            "convectionFan1Area": 0,
            "convectionFan2Active": False,
            "convectionFan2Level": 0,
            "convectionFan2Area": 0,
            "RoomPowerRequest": 2,
            "heatingPower": 75,
        },
    }


@pytest.fixture
def mock_stove_list_html():
    """Return a mock stove list HTML response."""
    return """
    <html>
        <body>
            <div class="stove" data-stove='{"stoveId": "12345", "name": "Test Stove"}'>
                <a href="/logout">Logout</a>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def mock_coordinator(mock_stove_state):
    """Return a mock coordinator."""
    with patch(
        "custom_components.rika_firenet.core.RikaFirenetCoordinator"
    ) as mock_coord:
        coordinator = MagicMock()
        coordinator.last_update_success = True
        coordinator.last_update_success_time = None
        coordinator.data = {}
        coordinator.platforms = ["climate", "sensor", "switch", "number", "binary_sensor"]

        # Mock stove
        mock_stove = MagicMock()
        mock_stove.get_id.return_value = "12345"
        mock_stove.get_name.return_value = "Test Stove"
        mock_stove.get_state.return_value = mock_stove_state
        mock_stove.get_stove_temperature.return_value = 85.5
        mock_stove.get_stove_thermostat.return_value = 22.0
        mock_stove.get_room_temperature.return_value = 21.2
        mock_stove.is_stove_on.return_value = True
        mock_stove.is_stove_burning.return_value = True

        coordinator.get_stoves.return_value = [mock_stove]
        coordinator.get_default_temperature.return_value = 21

        mock_coord.return_value = coordinator
        yield coordinator


@pytest.fixture
def mock_requests():
    """Mock requests library."""
    with patch("custom_components.rika_firenet.core.requests") as mock_req:
        session = MagicMock()
        mock_req.session.return_value = session

        # Mock successful login
        login_response = MagicMock()
        login_response.status_code = 200
        login_response.text = '<a href="/logout">Logout</a>'
        session.post.return_value = login_response

        yield mock_req
