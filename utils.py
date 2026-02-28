from datetime import datetime, timedelta, timezone


def parse_time_from_str(duration: str) -> timedelta:
    """
        raises: ValueError
    """
    units = {'m': 'minutes', 'h': 'hours', 'd': 'days'}
    unit = duration[-1]
    if unit not in units:
        raise ValueError(f"Unsupported time unit '{unit}'. Use m, h, or d.")
    value = int(duration[:-1])
    return timedelta(**{units[unit]: value})


def determine_window(duration: timedelta) -> tuple[datetime, datetime]:
    start = datetime.now(timezone.utc)
    end = start + duration
    return start, end
