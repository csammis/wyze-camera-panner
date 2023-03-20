"""API into the docker-wyze-bridge controlling the cameras"""

import configparser
import logging
import asyncio
from pathlib import Path
from aiohttp import ClientSession, ClientConnectionError, ClientResponseError

_LOGGER = logging.getLogger(__name__)


class WyzeCamera:
    """Representation of a Wyze camera connected via the bridge."""

    def __init__(
        self, host: str, port: int, camera_name: str, session: ClientSession,
        config_path: str
    ) -> None:
        """Initialize the camera representation."""
        self.host = host
        self.port = port
        self.camera_name = camera_name
        self._session = session
        self._config_path = config_path

    def _get_api_base_url(self) -> str:
        """Get the URL to the API base for this camera."""
        return f"http://{self.host}:{self.port}/api/{self.camera_name.lower()}"

    async def _is_camera_ready(self) -> bool:
        """Determine whether the bridge is ready for control commands"""
        try:
            url = f"{self._get_api_base_url()}/status"
            async with self._session.get(url) as resp:
                if resp.status == 200:
                    resp_data = await resp.json()
                    _LOGGER.debug("%s: %s", url, resp_data)
                    status = resp_data.get("status")
                    if status is not None:
                        return str(status).lower() == "connected"
        except ClientConnectionError:
            pass
        except ClientResponseError:
            pass
        return False

    async def _start_camera_connection(self) -> bool:
        """Issue a start command to the camera."""
        try:
            url = f"{self._get_api_base_url()}/start"
            async with self._session.get(url) as resp:
                if resp.status == 200:
                    resp_data = await resp.json()
                    _LOGGER.debug("%s: %s", url, resp_data)
                    status = resp_data.get("status")
                    if status is not None:
                        return bool(status)
        except ClientConnectionError:
            pass
        except ClientResponseError:
            pass
        return False

    async def _prepare_for_control(self) -> bool:
        """
        Get the camera control connected if it isn't already. This will start a connection
        thread on the bridge which may take 2-3 seconds to get going, so this function
        polls status for up to five seconds before giving up.
        """
        connected = await self._is_camera_ready()
        if connected is False:
            if await self._start_camera_connection():
                for _ in range(10):
                    if await self._is_camera_ready():
                        return True
                    await asyncio.sleep(0.5)
        return connected

    async def get_camera_mac(self) -> str | None:
        """Get the MAC address for this camera."""
        try:
            async with self._session.get(self._get_api_base_url()) as resp:
                if resp.status != 200:
                    return None
                resp_data = await resp.json()
                _LOGGER.debug("%s: %s", "get_camera_mac", resp_data)
                camera_info = resp_data.get("camera_info")
                if camera_info is not None:
                    basic_info = camera_info.get("basicInfo")
                    if basic_info is not None:
                        return str(basic_info.get("mac"))
        except ClientConnectionError:
            pass
        except ClientResponseError:
            pass
        return None

    async def get_camera_model(self) -> str | None:
        """Get the model for this camera."""
        try:
            async with self._session.get(self._get_api_base_url()) as resp:
                if resp.status != 200:
                    return None
                resp_data = await resp.json()
                _LOGGER.debug("%s: %s", "get_camera_model", resp_data)
                camera_info = resp_data.get("camera_info")
                if camera_info is not None:
                    basic_info = camera_info.get("basicInfo")
                    if basic_info is not None:
                        return str(basic_info.get("model"))
                return None
        except ClientConnectionError:
            return None
        except ClientResponseError:
            return None

    async def get_camera_rtsp_url(self) -> str | None:
        """Get the RTSP url for this camera to pass to ffmpeg."""
        try:
            async with self._session.get(self._get_api_base_url()) as resp:
                if resp.status != 200:
                    return None
                resp_data = await resp.json()
                _LOGGER.debug("%s: %s", "RTSP fetch", resp_data)
                return str(resp_data.get("rtsp_url"))
        except ClientConnectionError:
            return None
        except ClientResponseError:
            return None

    async def is_camera_in_fake_privacy_mode(self) -> bool:
        """
        Determines whether the camera is in its fake privacy mode
        """
        config = self._load_config()
        return config.getboolean(self.camera_name, "private", fallback=False)

    async def _send_camera_command(self, endpoint: str) -> bool:
        """Send a control command to the camera."""
        try:
            url = f"{self._get_api_base_url()}/{endpoint}"
            if await self._prepare_for_control():
                async with self._session.get(url) as resp:
                    if resp.status == 200:
                        resp_data = await resp.json()
                        _LOGGER.debug("%s: %s", url, resp_data)
                        if resp_data.get("status") == "success":
                            return True
        except ClientConnectionError:
            pass
        except ClientResponseError:
            pass
        return False

    async def set_camera_to_fake_privacy_mode(self) -> bool:
        """
        Set the camera to pan itself so it's looking at its own butt
        """
        if await self._send_camera_command("set_action_down"):
            self._write_config(is_private=True)
            return True
        return False

    async def set_camera_to_straight_ahead(self) -> bool:
        """Set the camera to point straight ahead """
        if await self._send_camera_command("reset_rotation"):
            self._write_config(is_private=False)
            return True
        return False

    def _write_config(self, is_private: bool) -> None:
        """Write the configuration settings to a file."""
        config = self._load_config()
        config.set(self.camera_name, "private", str(is_private))
        Path(self._config_path).mkdir(exist_ok=True, parents=True)
        with open(self._config_path, "wt", encoding="utf-8") as handle:
            config.write(handle)

    def _load_config(self) -> configparser.ConfigParser:
        """
        Get a ConfigParser from the config_path file or sensible defaults if it does not exist.
        """
        retval = configparser.ConfigParser()
        retval.read_dict({
            "General": {
                "version": 1.0
            },
            self.camera_name: {
                "private": False
            }
        })
        retval.read(self._config_path)
        return retval
