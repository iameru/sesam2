from .utils import time_now
from .config import config
from .models import JWTClaims, JWTResponse, JWTDoorGrant
from jose import JWTError, jwt
from typing import Annotated, List
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
from pydantic import BaseModel, ValidationError
from passlib.context import CryptContext
from .db.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_token(user: User) -> JWTResponse:
    valid_until = time_now() + config.jwt_valid_token_time

    jwt_door_grants = [
        JWTDoorGrant(
            door_uuid=door_grant.door_uuid,
            weekday=door_grant.weekday,
            grant_start=door_grant.grant_start,
            grant_end=door_grant.grant_end,
        )
        for door_grant in user.door_grants
    ]
    claims = JWTClaims(
        name=user.name,
        user_uuid=user.uuid,
        exp=valid_until,
        door_grants=jwt_door_grants,
        is_admin=user.is_admin,
    )

    token = jwt.encode(
        claims.dict(),
        config.jwt_secret_key,
        algorithm=config.jwt_algorithm,
    )
    return JWTResponse(access_token=token, expires=valid_until)


def validate_token(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> JWTClaims:
    """Validate a JWT and return the signed claims it contains."""
    try:
        claims_dict = jwt.decode(
            token,
            config.jwt_secret_key,
            algorithms=config.jwt_algorithm,
            options={"require_exp": True},
        )
        claims = JWTClaims.parse_obj(claims_dict)
    except (JWTError, ValidationError):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "invalid JWT",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if claims.exp <= time_now():
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "JWT expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return claims
