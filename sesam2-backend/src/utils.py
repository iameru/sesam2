from datetime import datetime
from .config import config
import secrets

def time_now():
    return datetime.now(config.timezone)

def create_shareable_registration_code(length: int = 8) -> str:
    """ we want this lowercase, without special characters, and 8 characters long"""
    random_string = secrets.token_urlsafe(length*2).lower().replace("-", "").replace("_", "").replace(".", "")
    return random_string[:length]
