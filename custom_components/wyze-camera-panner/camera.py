""" Instantiate an FFmpegCamera to display this camera's feed."""

from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import DiscoveryInfoType
from homeassistant.components.ffmpeg import CONF_EXTRA_ARGUMENTS, CONF_INPUT
from homeassistant.components.ffmpeg.camera import FFmpegCamera, DEFAULT_ARGUMENTS
from .const import DOMAIN, DATA_KEY_CAMERA, CONFIG_KEY_MAC
from .bridge import WyzeCamera


async def async_setup_entry(
    hass: HomeAssistant,
    config: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the FFmpegCamera entity for this camera."""
    name = config.data[CONF_NAME]
    mac = config.data[CONFIG_KEY_MAC]
    wyze_data = hass.data[DOMAIN][mac]
    camera: WyzeCamera = wyze_data[DATA_KEY_CAMERA]

    ffmpeg_config = {
        CONF_NAME: name,
        CONF_INPUT: await camera.get_camera_rtsp_url(),
        CONF_EXTRA_ARGUMENTS: DEFAULT_ARGUMENTS,
    }

    async_add_entities([FFmpegCamera(hass, ffmpeg_config)])
