from fastapi import FastAPI, Response
from .config import config
from .db import create_engine, get_session, models, create_user
from sqlmodel import SQLModel, select
from .utils import time_now
from .auth import create_token, validate_token, get_password_hash, verify_password, JWTClaims, JWTResponse, Depends
from typing import Annotated
from .models import DoorResponse, JSONResponse
from uuid import UUID
from datetime import datetime, time
from .physical import door
from uuid import uuid4

# TODO DELETED
from pathlib import Path
Path("db.sqlite3").unlink(missing_ok=True)

## create the database and the initial admin
SQLModel.metadata.create_all(create_engine())
with get_session() as session:
    admin_user = create_user(session,
                             username=config.admin_user,
                             hashed_password=get_password_hash(config.admin_user_password),
                             is_admin=True,
                             )
    # to be deleted ##########################
    normal_user = create_user(session, username='test', hashed_password=get_password_hash('test'))

    now = time_now()
    [session.add(door_grant) for door_grant in [
        models.DoorGrant(user_uuid=admin_user.uuid, door_uuid=uuid4(), weekday=1, grant_start=time(hour=8), grant_end=time(hour=16)),
        models.DoorGrant(user_uuid=admin_user.uuid, door_uuid=uuid4(), weekday=2, grant_start=time(hour=8), grant_end=time(hour=16)),
        models.DoorGrant(user_uuid=admin_user.uuid, door_uuid=uuid4(), weekday=4, grant_start=time(hour=8), grant_end=time(hour=9)),
        models.DoorGrant(user_uuid=admin_user.uuid, door_uuid=uuid4(), weekday=4, grant_start=time(hour=14), grant_end=time(hour=15)),
        models.DoorGrant(user_uuid=admin_user.uuid, door_uuid="001b823d-1f5c-4f39-9e74-015bb2dcef8f", weekday=now.isoweekday(), grant_start=time(hour=now.hour), grant_end=time(hour=23)),
        models.DoorGrant(user_uuid=normal_user.uuid, door_uuid=uuid4(), weekday=4, grant_start=time(hour=8), grant_end=time(hour=9)),
        models.DoorGrant(user_uuid=normal_user.uuid, door_uuid=uuid4(), weekday=4, grant_start=time(hour=14), grant_end=time(hour=15)),
    ]]
    # is for development only #################
    session.commit()


app = FastAPI()

from pydantic import BaseModel
class TokenRequest(BaseModel):
    username: str
    password: str

class CreateUserRequest(BaseModel):
    username: str
    password: str
    is_admin: bool = False


@app.post("/token")
async def token_login(data: TokenRequest) -> Response:
    username = data.username
    password = data.password
    with get_session() as session:
        user: models.User = session.exec(select(models.User).where(models.User.name == username)).one_or_none()
        if user and verify_password(password, user.password):
            return create_token(user)
    return Response(status_code=401, content="Invalid credentials")


@app.post("/open", response_model=DoorResponse)
async def open_door(claim: Annotated[JWTClaims, Depends(validate_token)], door_id: UUID):
    """ We'll open the door """
    valid_grant = filter(
        lambda grant: grant.door_uuid == door_id 
        and grant.weekday == time_now().isoweekday() 
        and grant.grant_start <= time_now().time() <= grant.grant_end, claim.door_grants)

    if any(valid_grant):
        try:
            door.open(door_id)
        except Exception as e:
            return {"error": str(e)}
        return DoorResponse(message="door opened successful", status='success', door_id=door_id)
    return DoorResponse(message="access denied", status='error', door_id=door_id)


@app.post("/admin/create_user", response_model=JSONResponse)
async def create_a_user(claim: Annotated[JWTClaims, Depends(validate_token)], request: CreateUserRequest) -> Response:
    if claim.is_admin:
        with get_session() as session:
            user = create_user(
                session,
                username=request.username,
                hashed_password=get_password_hash(request.password),
                is_admin=request.is_admin
            )
            session.add(user)
            session.commit()
            return JSONResponse(status='success', message='User created successfully')
    return Response(status_code=401, content="Invalid credentials")


# can i check for is_admin earlier?
# @app.post("/admin/create_grants", response_model=JSONResponse)
