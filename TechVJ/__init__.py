import time
import asyncio

# Start time of the bot
START_TIME = time.time()

# Current version of the bot
__version__ = "1.0.0"


async def get_uptime() -> str:
    """
    Returns the uptime of the bot as a human-readable string.
    Async version in case you want to await this in async contexts.
    """
    elapsed = int(time.time() - START_TIME)
    hours, remainder = divmod(elapsed, 3600)
    minutes, seconds = divmod(remainder, 60)
    # Simulate async operation (optional)
    await asyncio.sleep(0)
    return f"{hours}h {minutes}m {seconds}s"
