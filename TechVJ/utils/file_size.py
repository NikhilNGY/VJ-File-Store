def human_size(size_bytes):
    """
    Convert bytes to a human-readable string.
    Example: 1024 -> 1 KB, 1048576 -> 1 MB
    """
    if size_bytes is None:
        return "0 Bytes"

    size_bytes = int(size_bytes)
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f} {units[i]}"