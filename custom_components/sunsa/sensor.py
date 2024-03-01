

"""Sunsa sensor."""


from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, EntityCategory, CONF_NAME, PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN, VALUE
from .coordinator import SunsaDataUpdateCoordinator
from .entity import SunsaEntity


@dataclass(frozen=True)
class SunsaSensorEntityDescription(SensorEntityDescription):
    """Sunsa sensor description."""

    round_state_value: bool = False
    state_fn: Callable[[StateType]] | None = None


# https://developers.home-assistant.io/docs/core/entity/#generic-properties
# noinspection PyArgumentList
SENSORS: tuple[SunsaSensorEntityDescription, ...] = (
    SunsaSensorEntityDescription(
        key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=0,
        state_fn=lambda data: data.get(VALUE)
    ),
    SunsaSensorEntityDescription(
        key="batteryPercentage",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Sunsa sensors."""
    coordinator: SunsaDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        SunsaSensor(coordinator, sunsa_device_id, description)
        for sunsa_device_id in coordinator.data
        for description in SENSORS
    )


class SunsaSensor(SunsaEntity, SensorEntity):
    """Representation of a Sunsa sensor."""

    entity_description: SunsaSensorEntityDescription

    def __init__(
        self,
        coordinator: SunsaDataUpdateCoordinator,
        sunsa_device_id: int,
        sensor_description: SunsaSensorEntityDescription,
    ) -> None:
        """Initialize the sensor entity."""
        super().__init__(
            coordinator,
            coordinator.data[sunsa_device_id][CONF_NAME],
            sensor_description,
            sunsa_device_id
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.device.get(self.entity_description.key)

        if self.entity_description.state_fn is not None:
            value = self.entity_description.state_fn(data)
        else:
            value = data

        self._attr_native_value = value

        self.async_write_ha_state()

    @property
    def device(self) -> dict[str, Any] | None:
        """Get the device data from the coordinator."""
        return self.coordinator.data.get(self._sunsa_device_id)
