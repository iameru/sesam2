from datetime import datetime
from .config import config

def time_now():
    return datetime.now(config.timezone)
