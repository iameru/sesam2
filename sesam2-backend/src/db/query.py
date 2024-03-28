from .models import User, DoorGrant
from sqlmodel import select
from ..auth import get_password_hash

def create_user(session, *, username, password, is_admin=False) -> User:
    if not session.exec(select(User).where(User.name == username)).first():
        user = User(name=username, password=get_password_hash(password), is_admin=is_admin)
        session.add(user)
        session.commit()
        return session.exec(select(User).where(User.name == username)).one()
