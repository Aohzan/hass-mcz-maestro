"""MCZ Maestro integration."""
import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.util import slugify

from .const import CONTROLLER, COORDINATOR, DOMAIN, PLATFORMS, UNDO_UPDATE_LISTENER
from .maestro import MaestroController

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the IP integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MCZ Maestro from a config entry."""
    config = entry.data

    controller = MaestroController(config[CONF_HOST], config[CONF_PORT])

    if not controller.connected:
        _LOGGER.error("Can't connect to MCZ")
        raise ConfigEntryNotReady
    _LOGGER.debug("Connected to MCZ")

    async def async_update_data():
        """Fetch data from API."""
        controller.send("C|RecuperoInfo")
        return controller.receive()

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(seconds=config[CONF_SCAN_INTERVAL]),
    )

    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    undo_listener = entry.add_update_listener(_async_update_listener)

    hass.data[DOMAIN][entry.entry_id] = {
        CONTROLLER: controller,
        COORDINATOR: coordinator,
        CONF_HOST: controller.host,
        CONF_PORT: controller.port,
        UNDO_UPDATE_LISTENER: undo_listener,
    }

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, controller.host + controller.port)},
        default_manufacturer="MCZ",
        default_model="Maestro",
        default_name=f"MCZ Maestro {controller.host}:{controller.port}",
    )

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *(
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            )
        )
    )

    hass.data[DOMAIN][entry.entry_id][UNDO_UPDATE_LISTENER]()

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class MczEntity(CoordinatorEntity):
    """Representation of a generic MCZ entity."""

    def __init__(
        self, controller: MaestroController, coordinator, name: str, command_name
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.controller = controller
        self._command_name = command_name

        self._attr_name = name
        self._attr_unique_id = slugify(
            "_".join(
                [
                    DOMAIN,
                    controller.host,
                    controller.port,
                    command_name,
                ]
            )
        )
        self._attr_device_info = {
            "identifiers": {(DOMAIN, controller.host + controller.port)},
            "via_device": (DOMAIN, controller.host + controller.port),
        }

        self._state = None
