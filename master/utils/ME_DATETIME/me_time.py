from django.conf import settings
from datetime import datetime
import pytz

def get_current_time():
    """
    Function: get_current_time()

    Description:
        This function retrieves the current time adjusted to the timezone specified in the Django settings.

    Returns:
        datetime: A datetime object representing the current time adjusted to the timezone specified in the Django settings.

    Dependencies:
        - pytz: Python library that provides timezone support
        - datetime: Python module that provides classes for manipulating dates and times
        - django.conf.settings: Django module that allows access to Django settings
    
    Usage:
        current_time = get_current_time()

    Notes:
        - Ensure that the Django settings include a `TIME_ZONE` variable set to the desired timezone string.
        - This function uses the settings.TIME_ZONE to determine the timezone.
    """
    utc_now = datetime.now()

    current_time = pytz.timezone(settings.TIME_ZONE)
    return utc_now.astimezone(current_time)