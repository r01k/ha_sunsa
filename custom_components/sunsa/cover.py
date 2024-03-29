

"""Sunsa cover."""


from __future__ import annotations

import voluptuous as vol
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
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    DEFAULT_SMART_HOME_DIRECTION,
    SERVICE_SET_ABSOLUTE_POSITION,
    ATTR_CURRENT_ABSOLUTE_POSITION,
    BLIND_TYPE,
    LOGGER
)
from .coordinator import SunsaDataUpdateCoordinator
from .entity import SunsaEntity

from pysunsa import CLOSED_POSITION, OPEN_POSITION, RIGHT, DOWN
from pysunsa.exceptions import PysunsaError

SERVICE_SET_POSITION_SCHEMA = {
    vol.Required(ATTR_POSITION): vol.All(
        vol.Range(min=-100, max=100),
        vol.All(int)
    )
}


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

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_SET_ABSOLUTE_POSITION,
        SERVICE_SET_POSITION_SCHEMA,
        "_async_update_cover",
    )
    LOGGER.debug("Registered cover services")


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
        self.sunsa = self.coordinator.sunsa
        LOGGER.debug("Instantiated cover: %s", device_name)

    @property
    def current_cover_position(self) -> int:
        """Return current position of cover."""
        return CLOSED_POSITION - abs(self.current_absolute_position)

    @property
    def current_absolute_position(self) -> int:
        """
        Return current absolute position of cover.
        Blind position range is [-100, 100] where -100 is closed left or up,
        100 is closed right or down and 0 is fully open.
        """
        return self.device.get(ATTR_POSITION)

    @property
    def is_closed(self) -> bool:
        """Return true if cover is closed, else False."""
        # Position 0 in Sunsa with means fully open
        return abs(self.current_cover_position) == OPEN_POSITION

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the detailed device state attributes."""
        return {
            ATTR_CURRENT_ABSOLUTE_POSITION: self.current_absolute_position,
        }

    @property
    def default_closing_direction(self) -> int:
        """
        Return the default closing direction of the blind.
        1 for right or down if a vertical or horizontal blind, respectively.
        -1 for left or up if a vertical or horizontal blind, respectively.
        """
        if self.device[DEFAULT_SMART_HOME_DIRECTION]["text"] in (RIGHT, DOWN):
            return 1
        else:
            return -1

    @property
    def icon(self) -> str | None:
        """Icon of the entity, based on blind type."""
        if self.device is not None:
            if self.device[BLIND_TYPE]["text"].lower() == "vertical":
                orientation = "vertical"
            else:
                orientation = "horizontal"

            icon_name = f"mdi:blinds-{orientation}"
            if self.is_closed:
                icon_name += "-closed"
            return icon_name

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Set the cover to the open position."""
        await self._async_update_cover(OPEN_POSITION)

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Set the cover to the open position."""
        await self._async_update_cover(CLOSED_POSITION * self.default_closing_direction)

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Set the cover to a specific position between 0 and 100."""
        await self._async_update_cover(
            (CLOSED_POSITION - int(kwargs[ATTR_POSITION])) *
            self.default_closing_direction
        )

    async def _async_update_cover(self, position: int) -> None:
        """Set the cover to the new position."""
        LOGGER.debug(
            "Moving cover %s to position %s",
            self.device_info[CONF_NAME],
            position
        )
        try:
            await self.coordinator.sunsa.update_device(self._sunsa_device_id, position)
        except PysunsaError:
            raise HomeAssistantError(
                f"Unable to reposition {self.name}"
            )
