

"""Sunsa cover."""


from __future__ import annotations

from typing import Any
from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)

from homeassistant.const import CONF_NAME
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CLOSED_POSITION,
    OPEN_POSITION,
    DOMAIN,
    DEFAULT_SMART_HOME_POISTION,
    RIGHT,
    LOGGER
)
from .coordinator import SunsaDataUpdateCoordinator
from .entity import SunsaEntity

from pysunsa.exceptions import PysunsaError


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Sunsa covers."""

    coordinator: SunsaDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        SunsaCover(coordinator, sunsa_device_id)
        for sunsa_device_id in coordinator.data
    )


class SunsaCover(SunsaEntity, CoverEntity):
    """Representation of a Sunsa cover."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_device_class = CoverDeviceClass.BLIND
    _attr_supported_features = (
            CoverEntityFeature.OPEN
            | CoverEntityFeature.CLOSE
            | CoverEntityFeature.SET_POSITION
    )

    def __init__(
        self,
        coordinator: SunsaDataUpdateCoordinator,
        sunsa_device_id: int,
    ) -> None:
        """Initialize the cover entity."""
        device_name = coordinator.data[sunsa_device_id][CONF_NAME]
        super().__init__(
            coordinator,
            device_name,
            sunsa_device_id
        )

    @property
    def current_cover_position(self) -> int:
        """Return current position of cover."""
        # Blind position is [-100 - 100] where -100 is closed in one direction,
        # 100 is closed in the other and 0 is completely open.
        return CLOSED_POSITION - abs(self.device.get(ATTR_POSITION))

    @property
    def is_closed(self) -> bool:
        """Return true if cover is closed, else False."""
        return abs(self.current_cover_position) == CLOSED_POSITION

    @property
    def default_closed_position(self) -> int:
        """Return the default closed position of the cover depending on the default \
        smart home position."""
        return CLOSED_POSITION \
            if self.device.get(DEFAULT_SMART_HOME_POISTION) == RIGHT else \
            -CLOSED_POSITION

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Set the cover to the open position."""
        await self._async_update_cover(OPEN_POSITION)

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Set the cover to the open position."""
        await self._async_update_cover(self.default_closed_position)

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Set the cover to a specific position."""
        await self._async_update_cover(
            # Sunsa API accepts positions in multiple of 10
            round(int(kwargs[ATTR_POSITION]), -1)
        )

    async def _async_update_cover(self, position: int) -> None:
        """Set the cover to the new position."""
        try:
            await self.coordinator.sunsa.update_device(self._sunsa_device_id, position)
        except PysunsaError:
            raise HomeAssistantError(
                f"Unable to reposition {self.name}"
            )
