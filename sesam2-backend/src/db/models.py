from typing import Optional
from uuid import uuid4, UUID
from sqlmodel import Field, SQLModel
from datetime import datetime
from ..utils import time_now


class User(SQLModel, table=True):
    uuid: UUID | None = Field(primary_key=True, default_factory=uuid4)
    name: str
    password: str
    created: Optional[datetime] = Field(default_factory=time_now)

class Administrator(SQLModel, table=True):
    uuid: UUID | None = Field(primary_key=True, default_factory=uuid4)
    name: str
    role: str
    created: Optional[datetime] = Field(default_factory=time_now)
