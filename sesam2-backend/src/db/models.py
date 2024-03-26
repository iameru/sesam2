from typing import Optional, List
from uuid import uuid4, UUID
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, time
from ..utils import time_now


class DBModel(SQLModel):
    created: Optional[datetime] = Field(default_factory=time_now)
    updated: datetime | None = None


class DoorGrant(DBModel, table=True):
    uuid: UUID | None = Field(primary_key=True, default_factory=uuid4)
    user_uuid: UUID = Field(foreign_key="user.uuid")
    door_uuid: UUID
    weekday: int
    grant_start: time
    grant_end: time

    user: "User" = Relationship(back_populates="door_grants")


class User(DBModel, table=True):
    uuid: UUID | None = Field(primary_key=True, default_factory=uuid4)
    name: str
    password: str
    is_admin: bool = False

    door_grants: List[DoorGrant] = Relationship(back_populates="user")
