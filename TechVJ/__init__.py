import time
import asyncio
from datetime import datetime

# Application start time
StartTime = datetime.utcnow()

# Application version
__version__ = "1.0.0"

async def get_uptime() -> str:
    """
    Returns the uptime of the bot as a human-readable string.
    Async version in case you want to await this in async contexts.
    """
    elapsed = int(time.time() - StartTime.timestamp())  # Use StartTime correctly
    hours, remainder = divmod(elapsed, 3600)
    minutes, seconds = divmod(remainder, 60)
    # Simulate async operation (optional)
    await asyncio.sleep(0)
    return f"{hours}h {minutes}m {seconds}s"
