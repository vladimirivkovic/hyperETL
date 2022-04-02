import pytz
from datetime import datetime


def timestamp_to_datetime(ts):
    tz = pytz.timezone('UTC')
    return datetime.fromtimestamp(int(ts), tz).isoformat()
