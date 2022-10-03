"""Support for the MCZ sensors."""
from collections.abc import Mapping
import logging
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MaestroController, MczEntity
from .const import CONTROLLER, COORDINATOR, DOMAIN
from .tools import get_maestro_state_description

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the MCZ platform."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    controller = data[CONTROLLER]
    coordinator = data[COORDINATOR]

    entities = [
        MczStateEntity(controller, coordinator, name="State", command_name="state"),
        MczSensorEntity(
            controller,
            coordinator,
            "Temperature",
            "Ambient_Temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            unit_of_measurement=TEMP_CELSIUS,
        ),
    ]

    if entities:
        async_add_entities(entities)


class MczStateEntity(MczEntity, SensorEntity):
    """Representation of a debug sensor."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> str:
        """Return the state."""
        return get_maestro_state_description(self.coordinator.data["Stove_State"])

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return the state attributes."""
        if self.coordinator.data:
            return self.coordinator.data
        return {}


class MczSensorEntity(MczEntity, SensorEntity):
    """Representation of a MCZ sensor."""

    def __init__(
        self,
        controller: MaestroController,
        coordinator,
        name,
        command_name,
        device_class: SensorDeviceClass,
        unit_of_measurement: str,
    ):
        """Initialize the sensor."""
        super().__init__(controller, coordinator, name, command_name)
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit_of_measurement

    @property
    def native_value(self) -> float:
        """Return the state."""
        return self.coordinator.data[self._command_name]
