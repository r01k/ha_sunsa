

"""Config flow for Sunsa integration."""


from __future__ import annotations

import asyncio
from typing import Any

from aiohttp.client_exceptions import ClientConnectorError
from pysunsa import Pysunsa
from pysunsa.exceptions import PysunsaError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import (
    CONF_EMAIL,
    CONF_API_KEY
)
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, LOGGER, USER_ID


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sunsa."""

    VERSION = 1

    async def validate_user_input(
        self,
        user_input: dict[str, Any],
        errors: dict[str, str],
        description_placeholders: dict[str, str] | Any = None,
    ):
        sunsa = Pysunsa(
            async_get_clientsession(self.hass),
            userid=user_input[USER_ID],
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
            if isinstance(error, PysunsaError) and error.args[0] == 401:
                errors["base"] = "invalid_auth"
            else:
                errors["base"] = "cannot_connect"
            description_placeholders["error_detail"] = str(error.args)
        except Exception as error:  # pylint: disable=broad-except
            LOGGER.exception("Unexpected exception: %s", error)
            errors["base"] = "unknown"
            description_placeholders["error_detail"] = str(error.args)
        else:
            return devices

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        placeholders: dict[str, str] = {}

        if user_input is not None:

            if await self.validate_user_input(
                user_input,
                errors,
                description_placeholders=placeholders
            ):
                await self.async_set_unique_id(
                    user_input[CONF_EMAIL].lower(),
                    raise_on_progress=False
                )
                self._abort_if_unique_id_configured(updates=user_input)

                return self.async_create_entry(
                    title=user_input[CONF_EMAIL].lower(),
                    data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): str,
                    vol.Required(USER_ID): int,
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            description_placeholders=placeholders,
            errors=errors,
        )

    async def async_step_reauth(
            self,
            user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Perform reauth upon an API authentication error."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm(
            user_input=user_input,
        )

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, Any] | None,
    ) -> FlowResult:
        """Dialog that informs the user that reauth is required."""
        assert self._reauth_entry

        errors: dict[str, str] = {}
        placeholders: dict[str, str] = {}

        if user_input is None or not await self.validate_user_input(
            user_input,
            errors,
            description_placeholders=placeholders
        ):
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=vol.Schema(
                    {vol.Required(USER_ID): int,
                     vol.Required(CONF_API_KEY): str}
                ),
                description_placeholders=placeholders,
                errors=errors,
            )

        self.hass.config_entries.async_update_entry(self._reauth_entry, data=user_input)
        await self.hass.config_entries.async_reload(self._reauth_entry.entry_id)
        return self.async_abort(reason="reauth_successful")