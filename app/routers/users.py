from typing import Annotated

from fastapi import APIRouter, status, Depends, Path, HTTPException
from sqlmodel import Session

from app.auth import get_current_active_user
from app.crud.user import get_user_by_id
from app.database import get_session
from app.models import UserPublic, User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic, status_code=status.HTTP_200_OK)
def user_me(
        current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/{user_id}", response_model=UserPublic, status_code=status.HTTP_200_OK)
def find_user(
        user_id: Annotated[int, Path(title="The users.py ID")],
        current_user: Annotated[User, Depends(get_current_active_user)],
        session: Session = Depends(get_session)
):
    user = get_user_by_id(session, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="Usuario não encontrado")

    return user
