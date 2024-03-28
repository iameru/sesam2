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

    user_uuid: UUID | None = Field(foreign_key="user.uuid")
    door_uuid: UUID
    group_uuid: UUID | None = Field(foreign_key="group.uuid")

    weekday: int
    grant_start: time
    grant_end: time

    group: "Group" = Relationship(back_populates="door_grants")
    user: "User" = Relationship(back_populates="door_grants")


class Group(DBModel, table=True):
    uuid: UUID | None = Field(primary_key=True, default_factory=uuid4)
    name: str = Field(index=True, unique=True)
    description: str

    door_grants: List[DoorGrant] = Relationship(back_populates="group")
    users: List["User"] = Relationship(back_populates="group")


class User(DBModel, table=True):
    uuid: UUID | None = Field(primary_key=True, default_factory=uuid4)
    group_uuid: UUID | None = Field(foreign_key="group.uuid")

    name: str = Field(index=True, unique=True)
    password: str
    is_admin: bool = False

    group: Group = Relationship(back_populates="users")
    door_grants: List[DoorGrant] = Relationship(back_populates="user")
