import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)

from .const import DOMAIN
from .core import RikaFirenetCoordinator, RikaFirenetStove
from .entity import RikaFirenetEntity

_LOGGER = logging.getLogger(__name__)

DEVICE_BINARY_SENSORS = [
    "connectivity",
]


async def async_setup_entry(hass, entry, async_add_entities):
    _LOGGER.info("setting up platform binary_sensor")
    coordinator: RikaFirenetCoordinator = hass.data[DOMAIN][entry.entry_id]

    binary_sensor_entities = []

    # Create binary sensors for each stove
    for stove in coordinator.get_stoves():
        binary_sensor_entities.extend(
            [
                RikaFirenetBinarySensor(entry, stove, coordinator, sensor)
                for sensor in DEVICE_BINARY_SENSORS
            ]
        )

    if binary_sensor_entities:
        async_add_entities(binary_sensor_entities, True)


class RikaFirenetBinarySensor(RikaFirenetEntity, BinarySensorEntity):
    def __init__(
        self,
        config_entry,
        stove: RikaFirenetStove,
        coordinator: RikaFirenetCoordinator,
        sensor_type,
    ):
        super().__init__(config_entry, stove, coordinator, sensor_type)
        self._sensor_type = sensor_type

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        if self._sensor_type == "connectivity":
            # Check if coordinator last update was successful
            return self._coordinator.last_update_success
        return None

    @property
    def device_class(self):
        """Return the device class of the binary sensor."""
        if self._sensor_type == "connectivity":
            return BinarySensorDeviceClass.CONNECTIVITY
        return None

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        if self._sensor_type == "connectivity":
            return "mdi:wifi" if self.is_on else "mdi:wifi-off"
        return None
