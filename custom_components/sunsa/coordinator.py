
# https://developers.home-assistant.io/docs/integration_fetching_data/#coordinated-single-api-poll-for-data-for-all-entities

"""Provides the Fully Kiosk Browser DataUpdateCoordinator."""
import asyncio
from typing import Any, cast

from pysunsa import Pysunsa
from pysunsa.exceptions import PysunsaError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import LOGGER, UPDATE_INTERVAL, IDDEVICE, APIURL


class SunsaDataUpdateCoordinator(DataUpdateCoordinator):
    """Sunsa update coordinator."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.sunsa = Pysunsa(
            async_get_clientsession(hass),
            entry.data[CONF_USERNAME],
            entry.data[CONF_API_KEY]
        )
        super().__init__(
            hass,
            LOGGER,
            name=entry.data[IDDEVICE],
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        try:
            async with asyncio.timeout(15):
                device_info = await self.sunsa.get_device_info(self.name)
                return cast(dict[str, Any], device_info)
        except PysunsaError as error:
            raise UpdateFailed(error) from error
