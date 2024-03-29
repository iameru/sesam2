from fastapi import FastAPI, Response
from .config import config
from .db import create_engine, get_session, models, create_user
from sqlmodel import SQLModel, select
from .utils import time_now, create_shareable_registration_code
from .auth import create_token, validate_token, get_password_hash, verify_password, JWTClaims, JWTResponse, Depends
from typing import Annotated
from .models import DoorResponse, JSONResponse, TokenRequest, RegistrationRequest, CreateUserRequest, CreateUserResponse
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
                             is_active=True,
                             )
    # to be deleted ##########################
    normal_user = create_user(session, username='test', hashed_password=get_password_hash('test'), is_active=True)

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


@app.post("/token")
async def token_login(data: TokenRequest) -> Response:
    username = data.username
    password = data.password
    with get_session() as session:
        user: models.User = session.exec(
                select(models.User)
                .where(models.User.name == username)
                .where(models.User.is_active == True)
            ).one_or_none()
        if user and verify_password(password, user.password):
            return create_token(user)
    return Response(status_code=401, content="Invalid credentials")


@app.post("/register")
async def register(data: RegistrationRequest) -> Response:

    with get_session() as session:
        registration_code = session.exec(
            select(models.RegistrationCode)
                .where(models.RegistrationCode.code == data.registration_code)
                .where(models.RegistrationCode.valid_until >= time_now())
        ).one_or_none()
        
        if not registration_code:
            return Response(status_code=401, content="Invalid registration code")
        user = registration_code.user
        user.registration_code = None
        user.is_active = True
        user.password = get_password_hash(data.password)
        session.add(user)
        session.delete(registration_code)
        session.commit()
        return Response(status_code=200, content="User registered successfully")
    return Response(status_code=401, content="Invalid credentials")


@app.post("/admin/create_user", response_model=CreateUserResponse)
async def create_a_user(claim: Annotated[JWTClaims, Depends(validate_token)], request: CreateUserRequest) -> Response:
    if claim.is_admin:
        with get_session() as session:
            if not session.exec(select(models.User).where(models.User.name == request.username)).first():
                user = models.User(
                    name=request.username,
                    is_admin=request.is_admin,
                    is_active=False,
                )

                registration_code = models.RegistrationCode(
                    code=create_shareable_registration_code(),
                    valid_until=datetime.now() + config.auth_valid_registration_code_time,
                )
                session.add(registration_code)
                user.registration_code = registration_code
                session.add(user)
                session.commit()

            return CreateUserResponse(status='success', message='User created successfully', registration_code=registration_code.code)
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
