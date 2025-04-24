import os
from datetime import datetime
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, status, Depends, HTTPException, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.auth import get_password_hash, authenticate_user, create_access_token, create_refresh_token, verify_token
from app.crud.auth import create_recovery_token, get_reset_by_token
from app.crud.user import get_user_by_email_or_username, create_user, get_user_by_id, update_user
from app.database import get_session
from app.models import UserPublic, UserCreate, PasswordResetEmail, PasswordReset

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


@router.post("/signin", status_code=status.HTTP_204_NO_CONTENT)
def signin(
        response: Response,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: Session = Depends(get_session)
):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    response.set_cookie("access_token", access_token, httponly=True, max_age=1800)
    response.set_cookie("refresh_token", refresh_token, httponly=True, max_age=7 * 24 * 3600)


@router.post("/refresh", status_code=status.HTTP_204_NO_CONTENT)
def refresh(response: Response, refresh_token: str = Cookie(None)):
    data = verify_token(refresh_token)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access = create_access_token({"sub": data["sub"]})
    response.set_cookie("access_token", new_access, httponly=True, max_age=1800)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(reset_email: PasswordResetEmail, session: Session = Depends(get_session)):
    user = get_user_by_email_or_username(session, reset_email.email, "")
    if user:
        token = uuid4().hex

        create_recovery_token(session, user.id, token)

        # TODO: Enviar e-mail com o link
        print("Token para reset:", token)

    return {"message": "Se o e-mail existir, enviaremos instruções."}


@router.post("/reset-password")
def reset_password(
    password_reset: PasswordReset,
    session: Session = Depends(get_session)
):
    reset = get_reset_by_token(session, password_reset.token)
    if not reset or reset.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token inválido ou expirado.")

    user = get_user_by_id(session, reset.user_id)

    if not user:
        raise HTTPException(status_code=400, detail="Usuário inválido.")

    user.password = get_password_hash(password_reset.password)
    update_user(session, user)

    return {"message": "Senha redefinida com sucesso."}
