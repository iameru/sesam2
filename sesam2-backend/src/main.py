from fastapi import FastAPI, Response
from .config import config
from .db import create_engine, get_session, create_user
from .db.query import log_door_stats
from .db.models import User, RegistrationCode, DoorGrant, Group
from sqlmodel import SQLModel, select, update
from .utils import time_now, create_shareable_registration_code
from .auth import create_token, validate_token, validate_admin_token, get_password_hash, verify_password, JWTClaims, JWTResponse, Depends
from typing import Annotated, List
from .models import DoorResponse, JSONResponse, TokenRequest, RegistrationRequest, CreateUserRequest, CreateUserResponse, UpdateUserRequest, DeleteUserRequest, CreateGroupRequest, DeleteGroupRequest, PutGrantRequest, UserGroupRequest, DeleteGroupRequest
from uuid import UUID
from datetime import datetime, time
from .physical import door
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware


if config.dev_mode:
    print("DEVELOPMENT MODE")
    # start with a fresh DB every time
    from pathlib import Path
    Path("db.sqlite3").unlink(missing_ok=True)
    SQLModel.metadata.create_all(create_engine())
    with get_session() as session:
        admin_user = create_user(session,
             username=config.admin_user,
             hashed_password=get_password_hash(config.admin_user_password),
             is_admin=True,
             is_active=True,
         )
        normal_user = create_user(session, username='test', hashed_password=get_password_hash('test'), is_active=True)
        session.add(DoorGrant(
            user_uuid=admin_user.uuid, 
            door_uuid="001b823d-1f5c-4f39-9e74-015bb2dcef8f",
            name="super door",
            weekday=time_now().isoweekday(),
            grant_start=time(hour=time_now().hour),
            grant_end=time(hour=23),
        ))
        session.commit()
else:
    SQLModel.metadata.create_all(create_engine())


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.app_domain] if not config.dev_mode else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/are-we-online")
async def info() -> Response:
    Response(status_code=200)


@app.post("/token")
async def token_login(data: TokenRequest) -> Response:
    username = data.username
    password = data.password
    with get_session() as session:
        user: User = session.exec(
                select(User)
                .where(User.name == username)
                .where(User.is_active == True)
            ).one_or_none()
        if user and verify_password(password, user.password):
            return create_token(user)
    return Response(status_code=401, content="Invalid credentials")


@app.post("/register")
async def register(data: RegistrationRequest) -> Response:

    with get_session() as session:
        registration_code = session.exec(
            select(RegistrationCode)
                .where(RegistrationCode.code == data.registration_code)
                .where(RegistrationCode.valid_until >= time_now())
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


@app.post("/admin/user", response_model=CreateUserResponse)
async def create_a_user(claim: Annotated[JWTClaims, Depends(validate_admin_token)], request: CreateUserRequest) -> Response:
    # if claim.is_admin:
    with get_session() as session:
        if not session.exec(select(User).where(User.name == request.username)).first():
            user = User(
                name=request.username,
                is_admin=request.is_admin,
                is_active=False,
            )

            registration_code = RegistrationCode(
                code=create_shareable_registration_code(),
                valid_until=datetime.now() + config.auth_valid_registration_code_time,
            )
            session.add(registration_code)
            user.registration_code = registration_code
            session.add(user)
            session.commit()

            return CreateUserResponse(status='success', message='User created successfully', registration_code=registration_code.code)
    return Response(status_code=400, content="User already exists")
    # return Response(status_code=401, content="Invalid credentials")


@app.patch("/admin/user")
async def update_user(claim: Annotated[JWTClaims, Depends(validate_admin_token)], request: UpdateUserRequest) -> Response:
    with get_session() as session:
        user: User = session.exec(select(User).where(User.name == request.username)).one_or_none()
        if not user:
            return Response(status_code=404, content="User not found")

        new_user_data = request.model_dump(exclude_unset=True)
        user.sqlmodel_update(new_user_data)
        session.add(user)
        session.commit()
        return JSONResponse(status='success', message='User updated successfully')


@app.delete("/admin/user")
async def delete_user(claim: Annotated[JWTClaims, Depends(validate_admin_token)], request: DeleteUserRequest) -> Response:
    with get_session() as session:
        user: User = session.exec(select(User).where(User.name == request.username)).one_or_none()
        if not user:
            return Response(status_code=404, content="User not found")
        session.delete(user)
        session.commit()
        return JSONResponse(status='success', message='User deleted successfully')


@app.post("/admin/group")
async def create_group(claim: Annotated[JWTClaims, Depends(validate_admin_token)], group: CreateGroupRequest) -> Response:
    with get_session() as session:
        if not session.exec(select(Group).where(Group.name == group.name)).first():
            group = Group(name=group.name, description=group.description)
            session.add(group)
            session.commit()
            return JSONResponse(status='success', message='Group created successfully')
    return Response(status_code=400, content="Group already exists")


@app.put("/admin/usergroup")
async def add_user_to_group(claim: Annotated[JWTClaims, Depends(validate_admin_token)], usergroup: UserGroupRequest) -> Response:
    with get_session() as session:
        user: User = session.exec(select(User).where(User.name == usergroup.username)).one_or_none()
        if not user:
            return Response(status_code=404, content="User not found")
        group = session.exec(select(Group).where(Group.name == usergroup.groupname)).one_or_none()
        if not group:
            return Response(status_code=404, content="Group not found")
        user.groups.append(group)
        session.add(user)
        session.commit()
        return JSONResponse(status='success', message='User added to group successfully')


@app.delete("/admin/usergroup")
async def remove_user_from_group(claim: Annotated[JWTClaims, Depends(validate_admin_token)], usergroup: UserGroupRequest) -> Response:
    with get_session() as session:
        user: User = session.exec(select(User).where(User.name == usergroup.username)).one_or_none()
        if not user:
            return Response(status_code=404, content="User not found")
        group = session.exec(select(Group).where(Group.name == usergroup.groupname)).one_or_none()
        if not group:
            return Response(status_code=404, content="Group not found")
        user.groups.remove(group)
        session.add(user)
        session.commit()
        return JSONResponse(status='success', message='User removed from group successfully')


@app.patch("/admin/group")
async def update_group(claim: Annotated[JWTClaims, Depends(validate_admin_token)], group: CreateGroupRequest) -> Response:
    with get_session() as session:
        group = session.exec(select(Group).where(Group.name == group.name)).one_or_none()
        if not group:
            return Response(status_code=404, content="Group not found")
        group.description = group.description
        session.add(group)
        session.commit()
        return JSONResponse(status='success', message='Group updated successfully')


@app.delete("/admin/group")
async def delete_group(claim: Annotated[JWTClaims, Depends(validate_admin_token)], group: DeleteGroupRequest) -> Response:
    with get_session() as session:
        group = session.exec(select(Group).where(Group.name == group.name)).one_or_none()
        if not group:
            return Response(status_code=404, content="Group not found")
        session.delete(group)
        session.commit()
        return JSONResponse(status='success', message='Group deleted successfully')


@app.put("/admin/grants")
async def add_grants(claim: Annotated[JWTClaims, Depends(validate_admin_token)], request: PutGrantRequest) -> Response:
    with get_session() as session:
        if request.target == 'user':
            user: User = session.exec(select(User).where(User.name == request.target_name)).one_or_none()
            if not user:
                return Response(status_code=404, content="User not found")
            for grant in user.door_grants:
                session.delete(grant)

            for request_grant in request.grants:
                grant = DoorGrant(
                    user_uuid=user.uuid,
                    door_uuid=request_grant.door_uuid,
                    name=request_grant.name,
                    weekday=request_grant.weekday,
                    grant_start=request_grant.grant_start,
                    grant_end=request_grant.grant_end,
                )
                session.add(grant)

            session.commit()
            return JSONResponse(status='success', message='Grants added successfully')
        elif request.target == 'group':
            group = session.exec(select(Group).where(Group.name == request.target_name)).one_or_none()
            if not group:
                return Response(status_code=404, content="Group not found")
            for grant in group.door_grants:
                session.delete(grant)

            for request_grant in request.grants:
                grant = DoorGrant(
                    group_uuid=group.uuid,
                    door_uuid=request_grant.door_uuid,
                    name=request_grant.name,
                    weekday=request_grant.weekday,
                    grant_start=request_grant.grant_start,
                    grant_end=request_grant.grant_end,
                )
                session.add(grant)

            session.commit()
            return JSONResponse(status='success', message='Grants added successfully')


@app.post("/open", response_model=DoorResponse)
async def open_door(claim: Annotated[JWTClaims, Depends(validate_token)], door_uuid: UUID):
    """ We'll open the door """

    def access(grants = List[DoorGrant]) -> bool:
        valid_grants = filter(
            lambda grant: grant.door_uuid == door_uuid 
            and grant.weekday == time_now().isoweekday() 
            and grant.grant_start <= time_now().time() <= grant.grant_end,
            grants
        )
        if any(valid_grants):
            return True
        return False

    def open_door(session = None, *, door_uuid: UUID) -> Response:
        try:
            door.open(door_uuid)
        except Exception as e:
            return {"error": str(e)}
        finally:
            if not session:
                with get_session() as session:
                    log_door_stats(session, door_uuid)
                    session.commit()
            else:
                log_door_stats(session, door_uuid)
                session.commit()
        return DoorResponse(message="door opened successful", status='success', door_uuid=door_uuid)

    if access(claim.door_grants):
        return open_door(door_uuid=door_uuid)
    else:
        with get_session() as session:
            user = session.exec(select(User).where(User.name == claim.name)).one()
            for group in user.groups:
                if access(group.door_grants):
                    return open_door(session=session, door_uuid=door_uuid)

    return Response(status_code=401, content="Access denied")
