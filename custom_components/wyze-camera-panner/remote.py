"""Remote entity for Wyze Camera Panning."""

from typing import Any
import asyncio
from collections.abc import Iterable
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.remote import (
        ATTR_NUM_REPEATS,
        ATTR_DELAY_SECS,
        DEFAULT_DELAY_SECS,
        )
from homeassistant.const import CONF_NAME, CONF_MODEL
from .const import DOMAIN, DATA_KEY_CAMERA, CONFIG_KEY_MAC
from .bridge import WyzeCamera
from . import CameraRemoteBase

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the RemoteEntity for this camera."""
    name = config.data[CONF_NAME]
    model = config.data[CONF_MODEL]
    mac = config.data[CONFIG_KEY_MAC]
    wyze_data = hass.data[DOMAIN][mac]
    camera: WyzeCamera = wyze_data[DATA_KEY_CAMERA]
    is_on = not await camera.is_camera_in_fake_privacy_mode()

    async_add_entities([CameraRemote(camera, name, mac, model, is_on)])


class CameraRemote(CameraRemoteBase):
    """Create a remote entity for a camera."""

    def __init__(
        self, camera: WyzeCamera, name: str, mac: str, model: str, is_on: bool
    ) -> None:
        """Initialize a CameraRemote."""
        super().__init__(name, mac, model)
        self._camera = camera
        self._current_activity = None
        self._is_on = is_on

    @property
    def is_on(self) -> bool | None:
        """Return the camera's 'on' state"""
        return self._is_on

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Handle the service call to turn this remote off."""
        await self._camera.set_camera_to_fake_privacy_mode()
        self._is_on = False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Handle the service call to turn this remote on."""
        await self._camera.set_camera_to_straight_ahead()
        self._is_on = True

    async def async_toggle(self, **kwargs: Any) -> None:
        """Handle the service call to toggle the remote off or on."""
        if self._is_on:
            await self.async_turn_off()
        else:
            await self.async_turn_on()

    @property
    def unique_id(self) -> str:
        """Return this entity's unique ID."""
        return f"{self._unique_id}"

    @property
    def name(self) -> str:
        """Return this entity's name."""
        return f"{self._name}"

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Process a command phrase being sent to the remote."""
        num_repeats = kwargs.get(ATTR_NUM_REPEATS)
        delay = kwargs.get(ATTR_DELAY_SECS, DEFAULT_DELAY_SECS)

        supported_commands = {
            "left": self._camera.pan_left,
            "right": self._camera.pan_right,
            "up": self._camera.pan_up,
            "down": self._camera.pan_down
        }

        for _ in range(num_repeats):
            for payload in command:
                if payload in supported_commands:
                    success = supported_commands[payload]()
                    if not success:
                        _LOGGER.warning("Unable to pan %s", payload)
                else:
                    _LOGGER.warning("%s is not a supported command", payload)

                await asyncio.sleep(delay)

    async def async_update(self) -> None:
        """Update the camera's is-on state."""
        self._is_on = not await self._camera.is_camera_in_fake_privacy_mode()
