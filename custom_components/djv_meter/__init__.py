"""The DJV-COM Meter integration."""
from __future__ import annotations

import logging
from datetime import time

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.event import async_track_time_change
from .coordinator import DJVMeterDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)
DOMAIN = "djv_meter"
PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up DJV-COM Meter from a config entry."""
    coordinator = DJVMeterDataUpdateCoordinator(
        hass,
        config=entry.data,
    )

    # Do initial update
    await coordinator.async_config_entry_first_refresh()

    # Schedule updates at 7 AM every day
    async def update_at_7am(now):
        """Update data at 7 AM."""
        await coordinator.async_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Schedule the update for 7 AM
    entry.async_on_unload(
        async_track_time_change(
            hass,
            update_at_7am,
            hour=7,
            minute=0,
            second=0,
        )
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok