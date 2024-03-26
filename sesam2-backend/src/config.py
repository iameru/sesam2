from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import timezone as tz, timedelta
from typing import Generator

class Config(BaseSettings):

    model_config = SettingsConfigDict(env_prefix='sesam2_')

    database_url: str
    secret_key: str

    timezone: tz = tz(timedelta(hours=1))

    jwt_valid_token_time: timedelta = timedelta(weeks=4)
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"


config = Config()
