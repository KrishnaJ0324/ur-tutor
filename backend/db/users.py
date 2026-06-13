"""
db/users.py
-----------
Thin repository for user accounts. Password hashing/verification lives in
auth/security.py; this module only persists what it's given.
"""
from sqlalchemy.orm import Session

from db.models import User


def get_by_username(session: Session, username: str) -> User | None:
    return session.query(User).filter(User.username == username).first()


def get_by_id(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def create(session: Session, username: str, hashed_password: str) -> User:
    user = User(username=username, hashed_password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
