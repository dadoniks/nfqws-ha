"""The NFQWS HA integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
import homeassistant.helpers.config_validation as cv
import homeassistant.helpers.entity_component as ec

from .const import DOMAIN, CONF_SSH_PORT, DEFAULT_SSH_PORT, CONF_STATUS_MONITORING
from .coordinator import NFQWSDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BUTTON]

SERVICE_RESTART = "restart"
SERVICE_START = "start"
SERVICE_STOP = "stop"

SERVICE_SCHEMA = vol.Schema({
    vol.Required("entry_id"): cv.string,
})


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the NFQWS HA component."""
    hass.data.setdefault(DOMAIN, {})

    async def async_handle_service(call: ServiceCall) -> None:
        entry_id = call.data["entry_id"]
        coordinator: NFQWSDataUpdateCoordinator | None = hass.data[DOMAIN].get(entry_id)
        if coordinator is None:
            raise ServiceValidationError(
                f"Config entry {entry_id} not found"
            )
        service = call.service
        if not await coordinator.async_execute_command(service):
            raise HomeAssistantError(f"Failed to execute {service}")

    hass.services.async_register(DOMAIN, SERVICE_RESTART, async_handle_service, SERVICE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_START, async_handle_service, SERVICE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_STOP, async_handle_service, SERVICE_SCHEMA)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NFQWS HA from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = NFQWSDataUpdateCoordinator(hass, entry)

    try:
        await coordinator.async_refresh()
        if not coordinator.data["available"]:
            _LOGGER.warning(
                "Initial connection to router failed, but integration will continue trying. "
                "Check your SSH credentials and network connectivity."
            )
    except Exception as err:
        _LOGGER.error("Error setting up NFQWS HA integration: %s", err)
        raise ConfigEntryNotReady from err

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok and entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)