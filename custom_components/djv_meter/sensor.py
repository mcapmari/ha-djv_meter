"""Sensor platform for DJV-COM Meter integration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfEnergy,
    UnitOfVolume,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from . import DOMAIN
from .coordinator import DJVMeterDataUpdateCoordinator

@dataclass
class DJVMeterSensorDescription(SensorEntityDescription):
    """Class describing DJV Meter sensor entities."""
    value_fn: callable = lambda x: x

SENSOR_TYPES: Final[tuple[DJVMeterSensorDescription, ...]] = (
    DJVMeterSensorDescription(
        key="meter_indications",
        name="Meter Indications",
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        device_class=SensorDeviceClass.GAS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: float(data["counter_indications"]),
    ),
    DJVMeterSensorDescription(
        key="last_day_consumption",
        name="Last Day",
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        device_class=SensorDeviceClass.GAS,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda data: float(data["curent_day"]),
    ),
    DJVMeterSensorDescription(
        key="current_month",
        name="Current Month",
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        device_class=SensorDeviceClass.GAS,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda data: float(data["sum"]),
    ),
    DJVMeterSensorDescription(
        key="gas_price",
        name="Gas Price",
        native_unit_of_measurement="MDL/m³",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda data: float(data["counter_settings"]["price"]["price"][0]),
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up DJV-COM Meter sensor based on a config entry."""
    coordinator: DJVMeterDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    
    for meter_data in coordinator.data["data"]:
        for description in SENSOR_TYPES:
            entities.append(
                DJVMeterSensor(
                    coordinator=coordinator,
                    description=description,
                    meter_data=meter_data,
                )
            )
    
    async_add_entities(entities)

class DJVMeterSensor(CoordinatorEntity, SensorEntity):
    """Representation of a DJV Meter sensor."""

    entity_description: DJVMeterSensorDescription

    def __init__(
        self,
        coordinator: DJVMeterDataUpdateCoordinator,
        description: DJVMeterSensorDescription,
        meter_data: dict,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._meter_data = meter_data
        
        # Create entity_id with consistent pattern for all sensors
        self.entity_id = f"sensor.djv_{description.key}_{meter_data['slave_uid']}"
        
        # Set the friendly name without the meter number
        self._attr_name = description.name
        
        self._attr_unique_id = f"{meter_data['tsd_id']}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, meter_data["tsd_id"])},
            "name": "Gas Meter",
            "manufacturer": "DJV-COM",
            "model": "Gas Meter",
        }

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        for meter_data in self.coordinator.data["data"]:
            if meter_data["tsd_id"] == self._meter_data["tsd_id"]:
                return self.entity_description.value_fn(meter_data)
        return None
