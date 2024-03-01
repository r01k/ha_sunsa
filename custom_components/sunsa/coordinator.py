
# https://developers.home-assistant.io/docs/integration_fetching_data/#coordinated-single-api-poll-for-data-for-all-entities

"""Provides the Sunsa DataUpdateCoordinator."""


import asyncio
from typing import Any

from pysunsa import Pysunsa
from pysunsa.exceptions import PysunsaError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import LOGGER, UPDATE_INTERVAL, DOMAIN, IDDEVICE


class SunsaDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator is responsible for updating devices."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.sunsa = Pysunsa(
            async_get_clientsession(hass),
            entry.data[CONF_USERNAME],
            entry.data[CONF_API_KEY]
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch devices data from Sunsa."""
        try:
            async with asyncio.timeout(15):
                devices = await self.sunsa.get_devices()
        except PysunsaError as error:
            raise UpdateFailed(error) from error

        # Updated info for all devices
        return {dev[IDDEVICE]: dev for dev in devices}
