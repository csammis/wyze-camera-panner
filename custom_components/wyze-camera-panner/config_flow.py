"""Config flow for Wyze Camera Panner."""

import logging
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_MODEL
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .bridge import WyzeCamera

from .const import DOMAIN, CONFIG_KEY_MAC, SUPPORTED_MODELS

_LOGGER = logging.getLogger(__name__)


class WyzeCameraPannerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Define the config flow for the Wyze Camera Panner."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Present the user configuration."""
        errors = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass, False)
            camera = WyzeCamera(
                user_input[CONF_HOST],
                user_input[CONF_PORT],
                user_input[CONF_NAME],
                session,
            )
            mac = await camera.get_camera_mac()
            if mac is None:
                errors["base"] = "status-not-found"
            else:
                _LOGGER.info("Setting up Wyze camera with MAC address %s", mac)
                model = await camera.get_camera_model()
                if model not in SUPPORTED_MODELS:
                    errors["base"] = "unsupported-model"
                else:
                    await self.async_set_unique_id(mac)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"{user_input[CONF_NAME]} Control",
                        data={
                            CONF_HOST: user_input[CONF_HOST],
                            CONF_PORT: user_input[CONF_PORT],
                            CONF_NAME: user_input[CONF_NAME],
                            CONF_MODEL: SUPPORTED_MODELS[model],
                            CONFIG_KEY_MAC: mac,
                        },
                    )

        user_input = user_input or {}
        data_schema = {
            vol.Required(CONF_HOST, default=user_input.get(CONF_HOST)): str,
            vol.Required(CONF_PORT, default=user_input.get(CONF_PORT)): int,
            vol.Required(CONF_NAME, default=user_input.get(CONF_NAME)): str,
        }

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=errors
        )
