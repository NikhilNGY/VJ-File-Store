def get_readable_time(seconds: int) -> str:
    """
    Converts seconds into a human-readable time format.
    
    Args:
        seconds (int): Time in seconds.
        
    Returns:
        str: Formatted time string.
    """
    if seconds <= 0:
        return "0s"

    time_list = []
    time_suffix_list = ["s", "m", "h", " days"]
    count = 0

    while count < 4:
        count += 1
        if count < 3:  # seconds -> minutes -> hours
            seconds, result = divmod(seconds, 60)
        else:  # hours -> days
            seconds, result = divmod(seconds, 24)
        time_list.append(int(result))
        if seconds == 0:
            break

    # Append suffixes
    time_list = [f"{val}{time_suffix_list[idx]}" for idx, val in enumerate(time_list)]

    # Format readable string
    readable_time = ""
    if len(time_list) == 4:
        readable_time += time_list.pop() + ", "
    time_list.reverse()
    readable_time += ": ".join(time_list)

    return readable_time