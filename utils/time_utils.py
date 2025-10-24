"""Time utility functions for the application"""

import pytz


def format_local_time(utc_datetime):
    """Convert UTC datetime to local timezone and format it

    Args:
        utc_datetime: datetime object in UTC timezone

    Returns:
        str: Formatted local time string (YYYY-MM-DD HH:MM:SS)
    """
    if not utc_datetime:
        return ""

    # Assume UTC if no timezone info
    if utc_datetime.tzinfo is None:
        utc_datetime = utc_datetime.replace(tzinfo=pytz.UTC)

    # Convert to local timezone
    local_datetime = utc_datetime.astimezone()
    return local_datetime.strftime("%Y-%m-%d %H:%M:%S")
