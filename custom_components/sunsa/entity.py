

"""Base entity for the Sunsa integration."""


from __future__ import annotations


from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SunsaDataUpdateCoordinator


class SunsaEntity(CoordinatorEntity[SunsaDataUpdateCoordinator], Entity):
    """Defines a Sunsa entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SunsaDataUpdateCoordinator,
        device_name: str,
        entity_description: EntityDescription,
        sunsa_device_id: int,

        ) -> None:
        """Initialize the Sunsa entity."""
        super().__init__(coordinator=coordinator)

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_name)},
            name=device_name,
            manufacturer=DOMAIN,
        )
        self._sunsa_device_id = sunsa_device_id
        self.entity_description = entity_description
        self._attr_unique_id = f"{device_name}-{entity_description.key}"
