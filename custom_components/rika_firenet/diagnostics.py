"""Diagnostics support for Rika Firenet."""
import logging
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_USERNAME, CONF_PASSWORD, DOMAIN
from .core import RikaFirenetCoordinator

_LOGGER = logging.getLogger(__name__)

# Keys to redact from diagnostics
TO_REDACT = {
    CONF_USERNAME,
    CONF_PASSWORD,
    "email",
    "password",
    "stoveID",
    "stoveId",
    "id",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: RikaFirenetCoordinator = hass.data[DOMAIN][entry.entry_id]

    diagnostics_data = {
        "entry": {
            "title": entry.title,
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": entry.options,
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "last_update_time": (
                coordinator.last_update_success_time.isoformat()
                if coordinator.last_update_success_time
                else None
            ),
            "platforms": coordinator.platforms,
        },
        "stoves": [],
    }

    # Add stove information
    for stove in coordinator.get_stoves():
        stove_state = stove.get_state()

        # Redact sensitive information from stove state
        stove_data = {
            "name": stove.get_name(),
            "state": async_redact_data(stove_state, TO_REDACT) if stove_state else None,
        }

        diagnostics_data["stoves"].append(stove_data)

    return diagnostics_data
