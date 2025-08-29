import asyncio
import logging
import aiohttp
import traceback
from config import PING_INTERVAL, URL, MAX_FAILURES, ALERT_CALLBACK

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


async def ping_server():
    """
    Periodically ping the server URL to keep it alive.
    Implements exponential backoff on failures and alerts on multiple consecutive failures.
    """
    retry_delay = PING_INTERVAL
    consecutive_failures = 0

    while True:
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(URL) as resp:
                    logger.info("Pinged server with response: %s", resp.status)
                    # Reset on success
                    retry_delay = PING_INTERVAL
                    consecutive_failures = 0

        except asyncio.TimeoutError:
            logger.warning("Timeout while pinging the server URL!")
            consecutive_failures += 1
        except aiohttp.ClientError as e:
            logger.error("Client error while pinging server: %s", e)
            consecutive_failures += 1
        except Exception:
            logger.error("Unexpected error during server ping:\n%s", traceback.format_exc())
            consecutive_failures += 1

        # Trigger alert if failures exceed threshold
        if consecutive_failures >= MAX_FAILURES:
            logger.warning(
                "Server has failed %d times consecutively. Triggering alert.", consecutive_failures
            )
            if ALERT_CALLBACK:
                await ALERT_CALLBACK(URL, consecutive_failures)
            consecutive_failures = 0  # reset after alert

        # Exponential backoff for next ping attempt on failure
        await asyncio.sleep(retry_delay)
        retry_delay = min(retry_delay * 2, 3600)  # Max 1 hour backoff


async def start_keepalive():
    """
    Starts the keepalive ping task.
    Can be integrated in the main asyncio loop of your bot/server.
    """
    logger.info("Starting keepalive task...")
    asyncio.create_task(ping_server())
