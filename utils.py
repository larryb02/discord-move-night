from datetime import datetime, timedelta, timezone
import re

import httpx

_ALLOWED = re.compile(
    r"^https://(www\.imdb\.com/title/tt\d+|letterboxd\.com/film/[\w-]+)"
)

_OG_TITLE = re.compile(r'<meta[^>]+property="og:title"[^>]+content="([^"]+)"', re.IGNORECASE)


def validate_url(url: str) -> bool:
    return bool(_ALLOWED.match(url))


async def fetch_metadata(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()
    match = _OG_TITLE.search(response.text)
    if not match:
        raise ValueError(f"Could not extract title from {url}")
    return match.group(1)


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
