from .query import create_user
from sqlmodel import create_engine as sqlmodel_create_engine, Session
from sqlalchemy import Engine
from ..config import config
from contextlib import contextmanager
from typing import Generator

def create_engine() -> Engine:
    return sqlmodel_create_engine(config.database_url)

@contextmanager
def get_session() -> Generator[Session, None, None]:
    with Session(create_engine()) as session:
        yield session

