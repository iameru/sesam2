from pydantic import BaseModel, field_serializer
from datetime import datetime, time
from uuid import UUID
from typing import Literal
from enum import StrEnum

STATUS = Literal['success', 'error']

class DoorGrant(BaseModel):
    door_id: int
    weekday: int
    grant_start: time
    grant_end: time

    @field_serializer('grant_start', 'grant_end')
    def serialize_time(self, time: time):
        return time.isoformat()


class JWTClaims(BaseModel):
    name: str
    exp: datetime
    door_grants: list[DoorGrant] = []
    is_admin: bool = False


class JWTResponse(BaseModel):
    access_token: str
    expires: datetime


class DoorResponse(BaseModel):
    status: STATUS
    message: str | None
    door_id: UUID


from .db.models import User as DBUser, DoorGrant as DBDoorGrant

class CreateUserRequest(BaseModel):
    user: DBUser


class CreateUserResponse(BaseModel):
    status: STATUS
    message: str | None
    
