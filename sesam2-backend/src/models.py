from pydantic import BaseModel, field_serializer
from datetime import datetime, time
from uuid import UUID
from typing import Literal, List
from enum import StrEnum

STATUS = Literal['success', 'error']


class JWTDoorGrant(BaseModel):
    door_uuid: UUID
    weekday: int
    grant_start: time
    grant_end: time

    @field_serializer('grant_start', 'grant_end')
    def serialize_time(self, time: time):
        return time.isoformat()

    @field_serializer('door_uuid')
    def serialize_uuid(self, uuid: UUID):
        return str(uuid)


class JWTClaims(BaseModel):
    name: str
    exp: datetime
    door_grants: List[JWTDoorGrant] = []
    is_admin: bool = False


class PutGrantRequest(BaseModel):
    target: Literal['user', 'group']
    target_name: str
    grants: List[JWTDoorGrant]


class JWTResponse(BaseModel):
    access_token: str
    expires: datetime


class JSONResponse(BaseModel):
    status: STATUS
    message: str | None


class DoorResponse(JSONResponse):
    door_id: UUID


class CreateUserResponse(JSONResponse):
    user: str | None


class CreateUserResponse(JSONResponse):
    registration_code: str


class TokenRequest(BaseModel):
    username: str
    password: str


class RegistrationRequest(TokenRequest):
    registration_code: str


class UpdateUserRequest(BaseModel):
    username: str
    is_admin: bool | None = False
    is_active: bool | None = None


class CreateUserRequest(BaseModel):
    username: str
    is_admin: bool = False


class DeleteUserRequest(BaseModel):
    username: str


class CreateGroupRequest(BaseModel):
    name: str
    description: str


class DeleteGroupRequest(BaseModel):
    name: str
