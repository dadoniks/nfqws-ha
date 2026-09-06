"""Button platform for NFQWS Keenetic."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_STATUS_MONITORING
from .coordinator import NFQWSDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    coordinator: NFQWSDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        NFQWSStartButton(coordinator, entry),
        NFQWSStopButton(coordinator, entry),
        NFQWSRestartButton(coordinator, entry)
    ])

class NFQWSButtonBase(CoordinatorEntity[NFQWSDataUpdateCoordinator], ButtonEntity):
    """Base class for NFQWS buttons."""

    def __init__(self, coordinator: NFQWSDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        web_port = self._entry.data.get("web_port", 90)
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"{self.coordinator.data.get('manufacturer', 'Router')} - {self._entry.data['host']}",
            manufacturer=self.coordinator.data.get("manufacturer", "Unknown"),
            model=self.coordinator.data.get("model", "Router"),
            configuration_url=f"http://{self._entry.data['host']}:{web_port}/",
        )

class NFQWSStartButton(NFQWSButtonBase):
    """Representation of a NFQWS Start Button."""

    def __init__(self, coordinator: NFQWSDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_start"
        self._attr_icon = "mdi:play-circle"
        self.entity_id = f"button.nfqws_{entry.entry_id}_start"

    @property
    def translation_key(self) -> str:
        """Return the translation key for this entity."""
        return "nfqws_start_button"

    async def async_press(self) -> None:
        """Handle the button press."""
        success = await self.coordinator.async_execute_command("start")
        if success and self._entry.data.get(CONF_STATUS_MONITORING, False):
            await self.coordinator.async_request_refresh()

class NFQWSStopButton(NFQWSButtonBase):
    """Representation of a NFQWS Stop Button."""

    def __init__(self, coordinator: NFQWSDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_stop"
        self._attr_icon = "mdi:stop-circle"
        self.entity_id = f"button.nfqws_{entry.entry_id}_stop"

    @property
    def translation_key(self) -> str:
        """Return the translation key for this entity."""
        return "nfqws_stop_button"

    async def async_press(self) -> None:
        """Handle the button press."""
        success = await self.coordinator.async_execute_command("stop")
        if success and self._entry.data.get(CONF_STATUS_MONITORING, False):
            await self.coordinator.async_request_refresh()

class NFQWSRestartButton(NFQWSButtonBase):
    """Representation of a NFQWS Restart Button."""

    def __init__(self, coordinator: NFQWSDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_restart"
        self._attr_icon = "mdi:refresh"
        self.entity_id = f"button.nfqws_{entry.entry_id}_restart"

    @property
    def translation_key(self) -> str:
        """Return the translation key for this entity."""
        return "nfqws_restart_button"

    async def async_press(self) -> None:
        """Handle the button press."""
        success = await self.coordinator.async_execute_command("restart")
        if success and self._entry.data.get(CONF_STATUS_MONITORING, False):
            await self.coordinator.async_request_refresh()