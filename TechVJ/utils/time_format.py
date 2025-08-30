import asyncio

async def get_readable_time(seconds: int) -> str:
    """
    Convert seconds into a human-readable string asynchronously.
    Example: 93784 -> "1 days: 2h: 3m: 4s"
    """
    intervals = (
        ('days', 86400),  # 60 * 60 * 24
        ('h', 3600),      # 60 * 60
        ('m', 60),
        ('s', 1)
    )

    result = []
    for name, count in intervals:
        value, seconds = divmod(seconds, count)
        if value > 0 or (name == 's' and not result):  # Always include seconds
            result.append(f"{int(value)}{name}")
        # Yield control back to the event loop every step
        await asyncio.sleep(0)

    return ": ".join(result)
