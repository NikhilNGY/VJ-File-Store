import asyncio
import logging
import aiohttp
import traceback
from config import PING_INTERVAL, URL  # Make sure URL is defined in config

async def ping_server():
    """
    Periodically ping the server URL to keep it alive or monitor its status.
    """
    sleep_time = PING_INTERVAL
    while True:
        await asyncio.sleep(sleep_time)
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(URL) as resp:
                    logging.info(f"Pinged server with response: {resp.status}")
        except asyncio.TimeoutError:
            logging.warning("Couldn't connect to the site URL: Timeout occurred.")
        except Exception:
            logging.error("Error occurred while pinging server:\n" + traceback.format_exc())