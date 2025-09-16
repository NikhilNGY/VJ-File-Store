def humanbytes(size: int) -> str:
    """
    Converts a byte size into a human-readable format.
    
    Example:
        1024 -> 1 KiB
        1048576 -> 1 MiB
    """
    if not size:
        return "0 B"
    
    power = 1024
    n = 0
    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB']
    
    while size >= power and n < len(units) - 1:
        size /= power
        n += 1
    
    return f"{size:.2f} {units[n]}"