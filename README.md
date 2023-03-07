# wyze-camera-panner
Home Assistant component for panning a Wyze V3 camera via the docker-wyze-bridge

## Features
* Combines a camera view with a remote control for the camera
* Eliminates the need for manually setting up a `camera` or `camera-ffmpeg` in your `configuration.yaml`
* Toggle a "Privacy Mode" on and off

## Known Limitations
The "Privacy Mode" implemented by this integration is not Wyze's true Privacy Mode, but instead rotating the camera lens towards the base so that it cannot see anything.

## Requirements
### docker-wyze-bridge
This integration requires [docker-wyze-bridge](https://github.com/mrlt8/docker-wyze-bridge/) installed and set up to communicate with the cameras to be controlled.
### ffmpeg
wyze-camera-panner displays the camera feed using the [ffmpeg](https://www.home-assistant.io/integrations/ffmpeg/) integration which must be separately installed and configured.
## Installation
This component is intended to be installed with [HACS](https://hacs.xyz). This Github repository will have to be added to HACS as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories).

## Configuration
* `hostname` - The hostname of the docker-wyze-bridge controlling the camera
* `port` - The port of the docker-wyze-bridge's WebUI (default is `5000`)
* `name` - The camera's name as it was entered in the Wyze setup app
