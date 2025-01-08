"""The DJV-COM Meter integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from .coordinator import DJVMeterDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)
DOMAIN = "djv_meter"
PLATFORMS: list[Platform] = [Platform.SENSOR]

# Define update interval as a constant
UPDATE_INTERVAL = timedelta(minutes=360)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up DJV-COM Meter from a config entry."""
    coordinator = DJVMeterDataUpdateCoordinator(
        hass,
        config=entry.data,
        update_interval=UPDATE_INTERVAL,  # Pass the update interval
    )

    # Do initial update
    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:
        _LOGGER.warning("Initial update failed, coordinator will retry automatically")
        raise

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
