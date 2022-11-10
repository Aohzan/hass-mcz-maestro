"""Support for the MCZ switches."""
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MczEntity
from .const import CONTROLLER, COORDINATOR, DOMAIN

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
        MczSwitchEntity(controller, coordinator, "Mode Eco", "Eco_Mode", 41),
        MczSwitchEntity(controller, coordinator, "Mode Silencieux", "Silent_Mode", 45),
        MczSwitchEntity(controller, coordinator, "Mode Actif", "Active_Mode", 35),
        MczSwitchEntity(controller, coordinator, "Mode Dynamique", "Control_Mode", 40),
        MczSwitchEntity(controller, coordinator, "Mode Chrono", "Chronostat", 1111),
    ]
    if entities:
        async_add_entities(entities)


class MczSwitchEntity(MczEntity, SwitchEntity):
    """Representation of a MCZ switch."""

    def __init__(self, controller, coordinator, name, command_name, command_id):
        """Initialize the sensor."""
        super().__init__(controller, coordinator, name, command_name)
        self._command_id = command_id

    @property
    def is_on(self) -> bool:
        """Return the state."""
        return self.coordinator.data[self._command_name] == 1

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        self.controller.send(f"C|WriteParametri|{self._command_id}|1")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        self.controller.send(f"C|WriteParametri|{self._command_id}|0")
        await self.coordinator.async_request_refresh()
