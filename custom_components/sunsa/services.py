

"""Services for the Sunsa integration."""


from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv
import homeassistant.helpers.device_registry as dr
import homeassistant.helpers.entity_registry as er

from .const import (
    ATTR_POSITION,
    DOMAIN,
    SERVICE_SET_POSITION,
)
from .coordinator import SunsaDataUpdateCoordinator


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up the services for the Fully Kiosk Browser integration."""

    async def collect_coordinators(
        device_ids: list[str],
    ) -> list[SunsaDataUpdateCoordinator]:
        config_entries = list[ConfigEntry]()
        registry = dr.async_get(hass)
        for target in device_ids:
            device = registry.async_get(target)
            if device:
                device_entries = list[ConfigEntry]()
                for entry_id in device.config_entries:
                    entry = hass.config_entries.async_get_entry(entry_id)
                    if entry and entry.domain == DOMAIN:
                        device_entries.append(entry)
                if not device_entries:
                    raise HomeAssistantError(
                        f"Device '{target}' is not a {DOMAIN} device"
                    )
                config_entries.extend(device_entries)
            else:
                raise HomeAssistantError(
                    f"Device '{target}' not found in device registry"
                )
        coordinators = list[SunsaDataUpdateCoordinator]()
        for config_entry in config_entries:
            if config_entry.state != ConfigEntryState.LOADED:
                raise HomeAssistantError(f"{config_entry.title} is not loaded")
            coordinators.append(hass.data[DOMAIN][config_entry.entry_id])
        return coordinators

    async def async_set_position(call: ServiceCall) -> None:
        """Set the position of a Sunsa blind."""
        for coordinator in await collect_coordinators(call.data[ATTR_ENTITY_ID]):
            await coordinator.sunsa.update_device(
                call.data[ATTR_ENTITY_ID],
                call.data[ATTR_POSITION]
            )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_POSITION,
        async_set_position,
        schema=vol.Schema(
            vol.All(
                {
                    vol.Required(ATTR_ENTITY_ID): cv.ensure_list,
                    vol.Required(ATTR_POSITION): vol.Any(int)
                }
            )
        ),
    )
