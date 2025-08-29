async def humanbytes(size: int | float) -> str:
    """
    Convert bytes to a human-readable format (KiB, MiB, GiB, TiB).

    Args:
        size (int | float): Size in bytes.

    Returns:
        str: Human-readable size string.
    """
    if not size:
        return "0 B"

    power = 1024
    n = 0
    suffixes = ["B", "KiB", "MiB", "GiB", "TiB"]

    while size >= power and n < len(suffixes) - 1:
        size /= power
        n += 1

    return f"{size:.2f} {suffixes[n]}"
