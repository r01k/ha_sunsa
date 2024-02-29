"""Config flow for Fully Kiosk Browser integration."""
from __future__ import annotations

import asyncio
import json
from typing import Any

from aiohttp.client_exceptions import ClientConnectorError
from pysunsa import Pysunsa
from pysunsa.exceptions import PysunsaError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import (
    CONF_USERNAME,
    CONF_API_KEY,
    CONF_EMAIL,
    CONF_NAME
)
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import format_mac

from .const import DOMAIN, LOGGER, IDDEVICE


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fully Kiosk Browser."""

    VERSION = 1

    async def validate_user_input(
            self,
            user_input: dict[str, Any],
            errors: dict[str, str],
            description_placeholders: dict[str, str] | Any = None,
    ):
        sunsa = Pysunsa(
            async_get_clientsession(self.hass),
            userid=user_input[CONF_USERNAME],
            apikey=user_input[CONF_API_KEY]
        )

        try:
            async with asyncio.timeout(15):
                devices = await sunsa.get_devices()
        except (
                ClientConnectorError,
                PysunsaError,
                TimeoutError,
        ) as error:
            LOGGER.debug(error.args, exc_info=True)
            errors["base"] = "cannot_connect"
            description_placeholders["error_detail"] = str(error.args)
        except Exception as error:  # pylint: disable=broad-except
            LOGGER.exception("Unexpected exception: %s", error)
            errors["base"] = "unknown"
            description_placeholders["error_detail"] = str(error.args)
        else:
            return devices

    async def _create_entry(
        self,
        device_info: dict[str, Any],
        user_input: dict[str, Any],
    ) -> FlowResult | None:

        await self.async_set_unique_id(
            device_info[IDDEVICE],
            raise_on_progress=False
        )
        self._abort_if_unique_id_configured(updates=user_input)

        return self.async_create_entry(
            title=device_info[CONF_NAME],
            data={IDDEVICE: device_info[IDDEVICE]}
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        placeholders: dict[str, str] = {}

        if user_input is not None:

            devices = await self.validate_user_input(
                user_input,
                errors,
                description_placeholders=placeholders
            )
            for device in devices:
                result = await self._create_entry(
                    device_info=device,
                    user_input=user_input
                )
                # TODO How to create an entry for each device?
                return result

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): str,  # FIXME What to use for userid?
                    vol.Required(CONF_USERNAME): int,
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            description_placeholders=placeholders,
            errors=errors,
        )