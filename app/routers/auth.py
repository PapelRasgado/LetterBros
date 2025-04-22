import os
from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.auth import get_password_hash, authenticate_user, create_access_token
from app.crud.user import get_user_by_email_or_username, create_user
from app.database import get_session
from app.models import UserPublic, UserCreate, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def signup(
        user: UserCreate,
        session: Session = Depends(get_session)
):
    if user.invite_code != os.getenv("INVITE_CODE"):
        raise HTTPException(status_code=401, detail="Código de convite invalido")

    if get_user_by_email_or_username(session, user.email, user.username):
        raise HTTPException(status_code=400, detail="Email ou username já cadastrado")

    user.password = get_password_hash(user.password)
    user_db = create_user(session, user)

    return user_db


@router.post("/signin", response_model=Token, status_code=status.HTTP_200_OK)
def signin(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: Session = Depends(get_session)
):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username}
    )
    return Token(access_token=access_token, token_type="bearer")
