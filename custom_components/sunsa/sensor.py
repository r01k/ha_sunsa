

"""Sunsa sensor."""


from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfTemperature, EntityCategory, CONF_NAME, PERCENTAGE, ATTR_TEMPERATURE,
    ATTR_BATTERY_LEVEL
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN, VALUE, TEXT, DEFAULT_SMART_HOME_DIRECTION, LOGGER, BLIND_TYPE
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
        key="batteryPercentage",
        translation_key=ATTR_BATTERY_LEVEL,
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SunsaSensorEntityDescription(
        key=ATTR_TEMPERATURE,
        translation_key=ATTR_TEMPERATURE,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        state_fn=lambda data: data.get(VALUE)
    ),
    SunsaSensorEntityDescription(
        key=DEFAULT_SMART_HOME_DIRECTION,
        translation_key="default_smart_home_direction",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_fn=lambda data: data[TEXT].lower()
    ),
    SunsaSensorEntityDescription(
        key=BLIND_TYPE,
        translation_key="blind_type",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_fn=lambda data: data[TEXT]
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Sunsa sensors."""
    coordinator: SunsaDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    sensors = [
        SunsaSensor(coordinator, sunsa_device_id, description)
        for sunsa_device_id in coordinator.data
        for description in SENSORS
    ]
    async_add_entities(sensors)
    LOGGER.debug("Registered %s sensors", len(sensors))


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
        device_name = coordinator.data[sunsa_device_id][CONF_NAME]
        super().__init__(
            coordinator,
            device_name,
            sunsa_device_id,
            sensor_description.key
        )
        self.entity_description = sensor_description

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
