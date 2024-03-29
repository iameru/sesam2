from .models import User, DoorGrant, DoorStats
from sqlmodel import select
from ..utils import time_now
from uuid import UUID

def create_user(session, *, username, hashed_password, is_admin=False, is_active=False) -> User:
    
    if not session.exec(select(User).where(User.name == username)).first():
        user = User(name=username, password=hashed_password, is_admin=is_admin, is_active=is_active)
        session.add(user)
        session.commit()
        return session.exec(select(User).where(User.name == username)).one()


def log_door_stats(session, door_uuid: UUID):
    door = session.exec(select(DoorStats).where(DoorStats.door_uuid == door_uuid)).one_or_none()
    if not door:
        door = DoorStats(door_uuid=door_uuid)
    door.open_count += 1
    door.last_opened = time_now()
    session.add(door)
