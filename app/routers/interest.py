from typing import Annotated, Sequence

from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import Session

from app.auth import get_current_user
from app.crud.interest import get_interest_by_id_and_user, create_interest, delete_interest, get_users_by_movie_interest
from app.crud.movie import get_movie_by_id
from app.database import get_session
from app.models import UserPublic, User, MovieInterest

router = APIRouter(prefix="/movies/{movie_id}", tags=["interest"])


@router.post("/interest", status_code=status.HTTP_204_NO_CONTENT)
def interest_movie(
        movie_id: int,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Session = Depends(get_session)
):
    if get_movie_by_id(session, movie_id) is None:
        raise HTTPException(status_code=404, detail="Filme não encontrado")

    if get_interest_by_id_and_user(session, movie_id, current_user.id) is not None:
        raise HTTPException(status_code=400, detail="Usuario já manifestou interesse nesse filme")

    movie_interest = MovieInterest(
        movie_id=movie_id,
        user_id=current_user.id
    )

    create_interest(session, movie_interest)


@router.delete("/interest", status_code=status.HTTP_204_NO_CONTENT)
def delete_interest_movie(
        movie_id: int,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Session = Depends(get_session)
):
    if get_movie_by_id(session, movie_id) is None:
        raise HTTPException(status_code=404, detail="Filme não encontrado")

    movie_interest = get_interest_by_id_and_user(session, movie_id, current_user.id)

    if movie_interest is None:
        raise HTTPException(status_code=400, detail="Usuario não manifestou interesse nesse filme")

    delete_interest(session, movie_interest)


@router.get("/interests", response_model=Sequence[UserPublic], status_code=status.HTTP_200_OK)
def list_interest(
        movie_id: int,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Session = Depends(get_session)
):
    if get_movie_by_id(session, movie_id) is None:
        raise HTTPException(status_code=404, detail="Filme não encontrado")

    return get_users_by_movie_interest(session, movie_id)
