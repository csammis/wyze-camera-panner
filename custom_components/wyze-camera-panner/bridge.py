"""API into the docker-wyze-bridge controlling the cameras"""

from aiohttp import ClientSession, ClientConnectionError, ClientResponseError
import logging

_LOGGER = logging.getLogger(__name__)


class WyzeCamera:
    """Representation of a Wyze camera connected via the bridge."""

    def __init__(
        self, host: str, port: int, camera_name: str, session: ClientSession
    ) -> None:
        """Initialize the camera representation."""
        self.host = host
        self.port = port
        self.camera_name = camera_name
        self._session = session

    def _get_api_base_url(self) -> str:
        """Get the URL to the API base for this camera."""
        return f"http://{self.host}:{self.port}/api/{self.camera_name.lower()}"

    async def get_camera_mac(self) -> str | None:
        """Get the MAC address for this camera."""
        try:
            async with self._session.get(self._get_api_base_url()) as resp:
                if resp.status != 200:
                    return None
                resp_data = await resp.json()
                camera_info = resp_data.get("camera_info")
                if camera_info is not None:
                    basic_info = camera_info.get("basicInfo")
                    if basic_info is not None:
                        return str(basic_info.get("mac"))
                return None
        except ClientConnectionError:
            return None
        except ClientResponseError:
            return None

    async def get_camera_model(self) -> str | None:
        """Get the model for this camera."""
        try:
            async with self._session.get(self._get_api_base_url()) as resp:
                if resp.status != 200:
                    return None
                resp_data = await resp.json()
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
                return str(resp_data.get("rtsp_url"))
        except ClientConnectionError:
            return None
        except ClientResponseError:
            return None

    async def is_camera_in_fake_privacy_mode(self) -> bool:
        """Determines whether the camera is in its fake privacy mode, as understood by the status light value."""
        endpoint = f"{self._get_api_base_url()}/get_status_light"
        try:
            async with self._session.get(endpoint) as resp:
                if resp.status != 200:
                    return True  # sure, why not
                data = await resp.json()
                return int(data.get("response")) == 2
        except ClientConnectionError:
            return False
        except ClientResponseError:
            return False

    async def set_camera_to_fake_privacy_mode(self) -> bool:
        """Set the camera to pan itself so it's looking at its own butt and turn off status light."""
        endpoint = f"{self._get_api_base_url()}/set_action_down"
        try:
            async with self._session.get(endpoint) as resp:
                if resp.status == 200:
                    light_endpoint = f"{self._get_api_base_url()}/set_status_light_off"
                    async with self._session.get(light_endpoint) as light_resp:
                        return light_resp.status == 200
        except ClientConnectionError:
            return False
        except ClientResponseError:
            return False

    async def set_camera_to_straight_ahead(self) -> bool:
        """Set the camera to point straight ahead and turn on status light."""
        endpoint = f"{self._get_api_base_url()}/reset_rotation"
        try:
            async with self._session.get(endpoint) as resp:
                if resp.status == 200:
                    light_endpoint = f"{self._get_api_base_url()}/set_status_light_on"
                    async with self._session.get(light_endpoint) as light_resp:
                        return light_resp.status == 200
        except ClientConnectionError:
            return False
        except ClientResponseError:
            return False
