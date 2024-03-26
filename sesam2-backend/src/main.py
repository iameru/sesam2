from fastapi import FastAPI
from .config import config
from .db import create_engine, get_session, models
from sqlmodel import SQLModel, select
from .utils import time_now
from .auth import create_token, validate_token, get_password_hash, verify_password, JWTClaims, JWTResponse, Depends
from typing import Annotated
from .models import DoorGrant, DoorResponse
from uuid import UUID
from datetime import datetime, time
from .physical import door

## create the models
SQLModel.metadata.create_all(create_engine())


app = FastAPI()


def create_my_holy_dev_user():
    with get_session() as session:
        if not session.exec(select(models.User).where(models.User.name == "dev")).first():
            user = models.User(name="dev", password=get_password_hash("dev"))
            session.add(user)
            session.commit()
create_my_holy_dev_user()

door_grants=[
    DoorGrant(door_id=1, weekday=1, grant_start=time(10,0), grant_end=time(12,0)),
    DoorGrant(door_id=1, weekday=3, grant_start=time(10,0), grant_end=time(12,0)),
    DoorGrant(door_id=1, weekday=3, grant_start=time(14,0), grant_end=time(15,0)),
]


@app.post("/token", response_model=JWTResponse)
async def token_login(username: str, password: str):
    with get_session() as session:
        user = session.exec(select(models.User).where(models.User.name == username)).first()
        if user and verify_password(password, user.password):

            return create_token(user, door_grants=door_grants)

        return {"error": "Invalid user data"}


@app.post("/open", response_model=DoorResponse)
async def stuff(token: Annotated[JWTClaims, Depends(validate_token)], door_id: UUID):
    """ We'll open the door """
    try:
        door.open(door_id)
    except Exception as e:
        return {"error": str(e)}
    return DoorResponse(message="door opened successfull", status='success', door_id=door_id)


