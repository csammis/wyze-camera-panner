"""Wyze Camera Panner module."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.components.remote import RemoteEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo

from .bridge import WyzeCamera
from .const import DOMAIN, DATA_KEY_CAMERA, CONFIG_KEY_MAC

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.CAMERA, Platform.REMOTE]


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Set up the entry for the Wyze camera component."""
    hostname = config.data[CONF_HOST]
    port = config.data[CONF_PORT]
    name = config.data[CONF_NAME]
    mac = config.data[CONFIG_KEY_MAC]

    _LOGGER.info(
        "Setting up Wyze camera panning integration with camera named '%s' at host %s / port %s",
        name,
        hostname,
        port,
    )

    session = async_get_clientsession(hass, False)
    config_path = f"{hass.config.path(mac)}/wyze-camera.ini"
    camera = WyzeCamera(hostname, port, name, session, config_path)

    # Stash the camera for access by remote entity setup
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][mac] = {DATA_KEY_CAMERA: camera}

    await hass.config_entries.async_forward_entry_setups(config, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Unload a Wyze camera entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(config, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(config.data[CONFIG_KEY_MAC])
    return unload_ok


class CameraRemoteBase(RemoteEntity):
    """Base class for the CameraRemote."""

    def __init__(self, name: str, mac: str, model: str) -> None:
        """Initialize a CameraRemoteBase."""
        super().__init__()
        _LOGGER.debug(
            "Creating CameraRemoteBase with params %s %s %s", mac, name, model
        )
        self._unique_id = mac
        self._name = name
        self.model = model

    @property
    def device_info(self) -> DeviceInfo:
        """Get the DeviceInfo describing this camera."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._unique_id)},
            name=self._name,
            model=self.model,
            manufacturer="Wyze",
        )
