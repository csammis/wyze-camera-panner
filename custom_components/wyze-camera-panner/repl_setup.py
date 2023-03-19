"""Meant for sourcing in an asyncio REPL to make for less typing."""
import aiohttp
from bridge import WyzeCamera

session = aiohttp.ClientSession()
cam = WyzeCamera("192.168.86.160", 8300, "snoopy", session, "camera.ini")