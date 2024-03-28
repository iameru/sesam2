from .models import User, DoorGrant
from sqlmodel import select

def create_user(session, *, username, hashed_password, is_admin=False, is_active=False) -> User:
    
    if not session.exec(select(User).where(User.name == username)).first():
        user = User(name=username, password=hashed_password, is_admin=is_admin, is_active=is_active)
        session.add(user)
        session.commit()
        return session.exec(select(User).where(User.name == username)).one()
