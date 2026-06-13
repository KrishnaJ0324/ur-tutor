"""
auth/routes.py
--------------
Register / login / me endpoints. `/auth/token` follows the OAuth2 password flow
(form fields `username` + `password`) so it slots straight into Swagger's Authorize.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.deps import get_current_user
from auth.security import create_access_token, hash_password, verify_password
from db import users
from db.base import get_session
from db.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, session: Session = Depends(get_session)):
    username = req.username.strip()
    if len(username) < 3 or len(req.password) < 6:
        raise HTTPException(status_code=400,
                            detail="Username must be >= 3 chars and password >= 6 chars.")
    if users.get_by_username(session, username):
        raise HTTPException(status_code=409, detail="Username already taken.")
    user = users.create(session, username, hash_password(req.password))
    logger.info("registered user id=%s username=%r", user.id, user.username)
    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/token", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = users.get_by_username(session, form.username.strip())
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserResponse)
def me(current: User = Depends(get_current_user)):
    return UserResponse(id=current.id, username=current.username)
