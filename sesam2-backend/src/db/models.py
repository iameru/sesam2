from typing import Optional, List
from uuid import uuid4, UUID
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, time
from ..utils import time_now


class DBModel(SQLModel):
    created_at: Optional[datetime] = Field(default_factory=time_now)
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": time_now, "nullable": True}
    )


class DoorGrant(DBModel, table=True):
    uuid: UUID | None = Field(primary_key=True, default_factory=uuid4)

    user_uuid: UUID | None = Field(foreign_key="user.uuid")
    door_uuid: UUID
    group_uuid: UUID | None = Field(foreign_key="group.uuid")

    weekday: int
    grant_start: time
    grant_end: time
    name: str

    group: "Group" = Relationship(back_populates="door_grants")
    user: "User" = Relationship(back_populates="door_grants")


class UserGroupLink(SQLModel, table=True):
    user_uuid: UUID | None = Field(default=None, foreign_key="user.uuid", primary_key=True)
    group_uuid: UUID | None = Field(default=None, foreign_key="group.uuid", primary_key=True)


class Group(DBModel, table=True):
    uuid: UUID | None = Field(primary_key=True, default_factory=uuid4)
    name: str = Field(index=True, unique=True)
    description: str

    door_grants: List[DoorGrant] = Relationship(back_populates="group")

    users: List["User"] = Relationship(back_populates="groups", link_model=UserGroupLink)


class User(DBModel, table=True):
    uuid: UUID | None = Field(primary_key=True, default_factory=uuid4)
    name: str = Field(index=True, unique=True)
    password: str | None = None
    is_admin: bool = False
    is_active: bool = False

    groups: List[Group] = Relationship(back_populates="users", link_model=UserGroupLink)

    door_grants: List[DoorGrant] = Relationship(back_populates="user")

    registration_code_uuid: UUID | None = Field(foreign_key="registration_code.uuid")
    registration_code: "RegistrationCode" = Relationship(back_populates="user")


class RegistrationCode(DBModel, table=True):
    __tablename__ = "registration_code"
    uuid: UUID | None = Field(primary_key=True, default_factory=uuid4)

    code: str = Field(index=True, unique=True)
    valid_until: datetime

    user: User = Relationship(back_populates="registration_code")


class DoorStats(DBModel, table=True):
    door_uuid: UUID = Field(primary_key=True, default_factory=uuid4)
    last_opened: datetime | None = None
    open_count: int = 0
