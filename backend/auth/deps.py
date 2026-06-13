"""
auth/deps.py
------------
FastAPI dependencies for authentication. `get_current_user` is the gate every learning
endpoint depends on — the user's identity comes from the verified JWT, never from the
request body. The Swagger "Authorize" button drives the OAuth2 password flow against
`/auth/token`, so multi-user testing is point-and-click.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from auth.security import decode_token
from db import users
from db.base import get_session
from db.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = decode_token(token)
    if user_id is None:
        raise credentials_error
    user = users.get_by_id(session, user_id)
    if user is None:
        raise credentials_error
    return user
