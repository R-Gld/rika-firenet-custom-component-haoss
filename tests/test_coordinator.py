"""Test Rika Firenet coordinator."""
from unittest.mock import MagicMock, patch

import pytest
import requests

from custom_components.rika_firenet.core import (
    RikaFirenetCoordinator,
    RikaFirenetStove,
)
from custom_components.rika_firenet.exceptions import (
    RikaAuthenticationError,
    RikaConnectionError,
    RikaTimeoutError,
)


@pytest.fixture
def coordinator(hass):
    """Create a coordinator instance."""
    return RikaFirenetCoordinator(
        hass=hass,
        username="test@example.com",
        password="test_password",
        default_temperature=21,
        config_flow=True,
    )


@pytest.fixture
def mock_session():
    """Create a mock requests session."""
    session = MagicMock()
    return session


async def test_coordinator_init(hass):
    """Test coordinator initialization."""
    coordinator = RikaFirenetCoordinator(
        hass=hass,
        username="test@example.com",
        password="test_password",
        default_temperature=21,
        config_flow=True,
    )

    assert coordinator._username == "test@example.com"
    assert coordinator._password == "test_password"
    assert coordinator._default_temperature == 21
    assert coordinator._client is None
    assert coordinator._stoves is None


async def test_connect_success(coordinator, mock_session):
    """Test successful connection."""
    with patch("custom_components.rika_firenet.core.requests") as mock_requests:
        mock_requests.session.return_value = mock_session

        # Mock successful login response
        login_response = MagicMock()
        login_response.status_code = 200
        login_response.text = '<a href="/logout">Logout</a>'
        mock_session.post.return_value = login_response
        mock_session.cookies = {"connect.sid": "test_session_id"}

        coordinator._client = mock_session
        coordinator.connect()

        # Verify login was called with correct parameters
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        assert call_args[0][0].endswith("/web/login")
        assert call_args[1]["data"]["email"] == "test@example.com"
        assert call_args[1]["data"]["password"] == "test_password"


async def test_connect_authentication_error(coordinator, mock_session):
    """Test connection with authentication error."""
    with patch("custom_components.rika_firenet.core.requests") as mock_requests:
        mock_requests.session.return_value = mock_session

        # Mock failed login response
        login_response = MagicMock()
        login_response.status_code = 401
        login_response.text = "Login failed"
        mock_session.post.return_value = login_response

        coordinator._client = mock_session

        with pytest.raises(RikaAuthenticationError):
            coordinator.connect()


async def test_connect_timeout_error(coordinator, mock_session):
    """Test connection with timeout error."""
    with patch("custom_components.rika_firenet.core.requests") as mock_requests:
        mock_requests.session.return_value = mock_session

        # Mock timeout
        mock_session.post.side_effect = requests.exceptions.Timeout("Connection timeout")

        coordinator._client = mock_session

        with pytest.raises(RikaTimeoutError):
            coordinator.connect()


async def test_connect_connection_error(coordinator, mock_session):
    """Test connection with connection error."""
    with patch("custom_components.rika_firenet.core.requests") as mock_requests:
        mock_requests.session.return_value = mock_session

        # Mock connection error
        mock_session.post.side_effect = requests.exceptions.ConnectionError(
            "Connection failed"
        )

        coordinator._client = mock_session

        with pytest.raises(RikaConnectionError):
            coordinator.connect()


async def test_is_authenticated_true(coordinator, mock_session):
    """Test is_authenticated returns True when session has cookie."""
    coordinator._client = mock_session
    mock_session.cookies = {"connect.sid": "test_session_id"}

    assert coordinator.is_authenticated() is True


async def test_is_authenticated_false(coordinator, mock_session):
    """Test is_authenticated returns False when session has no cookie."""
    coordinator._client = mock_session
    mock_session.cookies = {}

    assert coordinator.is_authenticated() is False


async def test_get_default_temperature(coordinator):
    """Test get_default_temperature."""
    assert coordinator.get_default_temperature() == 21


async def test_stove_initialization():
    """Test stove initialization."""
    coordinator = MagicMock()
    stove = RikaFirenetStove(
        coordinator=coordinator, id="12345", name="Test Stove"
    )

    assert stove.get_id() == "12345"
    assert stove.get_name() == "Test Stove"
    assert stove._previous_temperature is None
    assert stove._state is None


async def test_stove_get_stove_temperature(mock_stove_state):
    """Test get_stove_temperature."""
    coordinator = MagicMock()
    stove = RikaFirenetStove(coordinator=coordinator, id="12345", name="Test Stove")
    stove._state = mock_stove_state

    assert stove.get_stove_temperature() == 85.5


async def test_stove_get_room_temperature(mock_stove_state):
    """Test get_room_temperature."""
    coordinator = MagicMock()
    stove = RikaFirenetStove(coordinator=coordinator, id="12345", name="Test Stove")
    stove._state = mock_stove_state

    assert stove.get_room_temperature() == 21.2


async def test_stove_is_burning_true(mock_stove_state):
    """Test is_stove_burning returns True when stove is running."""
    coordinator = MagicMock()
    stove = RikaFirenetStove(coordinator=coordinator, id="12345", name="Test Stove")
    stove._state = mock_stove_state

    # statusMainState = 4 (running)
    assert stove.is_stove_burning() is True


async def test_stove_is_burning_false(mock_stove_state):
    """Test is_stove_burning returns False when stove is off."""
    coordinator = MagicMock()
    stove = RikaFirenetStove(coordinator=coordinator, id="12345", name="Test Stove")
    stove._state = mock_stove_state
    stove._state["sensors"]["statusMainState"] = 1  # Off

    assert stove.is_stove_burning() is False


async def test_stove_get_status_text_running(mock_stove_state):
    """Test get_status_text returns 'running' when stove is running."""
    coordinator = MagicMock()
    stove = RikaFirenetStove(coordinator=coordinator, id="12345", name="Test Stove")
    stove._state = mock_stove_state

    # statusMainState = 4 (running)
    assert stove.get_status_text() == "running"


async def test_stove_get_status_frost_protection(mock_stove_state):
    """Test get_status_text returns 'frost_protection' when frost is active."""
    coordinator = MagicMock()
    stove = RikaFirenetStove(coordinator=coordinator, id="12345", name="Test Stove")
    stove._state = mock_stove_state
    stove._state["sensors"]["statusFrostStarted"] = True

    assert stove.get_status_text() == "frost_protection"
