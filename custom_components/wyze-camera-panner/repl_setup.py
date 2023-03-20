"""Meant for sourcing in an asyncio REPL to make for less typing."""
import logging
import sys
import aiohttp
from bridge import WyzeCamera
from bridge import _LOGGER

_LOGGER.setLevel(logging.DEBUG)
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)
_LOGGER.addHandler(stream)

session = aiohttp.ClientSession()
cam = WyzeCamera("192.168.86.160", 8300, "snoopy", session, "camera.ini")