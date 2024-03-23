

"""Base entity for the Sunsa integration."""


from __future__ import annotations

from typing import Any
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, IS_CONNECTED
from .coordinator import SunsaDataUpdateCoordinator


class SunsaEntity(CoordinatorEntity[SunsaDataUpdateCoordinator], Entity):
    """Defines a basic Sunsa entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SunsaDataUpdateCoordinator,
        device_name: str,
        sunsa_device_id: int,
        entity_description: str | None = None

        ) -> None:
        """Initialize the Sunsa entity."""
        super().__init__(coordinator=coordinator)

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_name)},
            name=device_name,  # Entity is part of the cover device
            manufacturer=DOMAIN.title(),
        )
        self._sunsa_device_id = sunsa_device_id
        self._attr_unique_id = str(sunsa_device_id)
        if entity_description:
            self._attr_unique_id += f"-{entity_description}"

    @property
    def available(self) -> bool:
        """Return the availability of the device that provides this sensor data."""
        return (super().available
                and self.device is not None
                and self.device.get(IS_CONNECTED) is True)

    @property
    def device(self) -> dict[str, Any] | None:
        """Get the device data from the coordinator."""
        return self.coordinator.data.get(self._sunsa_device_id)
