def human_size(size: int, units: list[str] = None) -> str:
    """
    Convert a size in bytes to a human-readable string.
    
    Args:
        size (int): Size in bytes.
        units (list[str], optional): List of units. Defaults to ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB'].

    Returns:
        str: Human-readable size string.
    """
    if units is None:
        units = ["bytes", "KB", "MB", "GB", "TB", "PB", "EB"]

    size = float(size)
    for unit in units:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} {units[-1]}"
