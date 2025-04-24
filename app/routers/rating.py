from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import Session

from app.auth import get_current_user
from app.crud.movie import get_movie_by_id
from app.crud.rating import create_or_update_rating, get_rating_by_id_and_user, delete_rating, get_movie_rating_summary
from app.database import get_session
from app.models import User, MovieRatingCreate

router = APIRouter(prefix="/movies/{movie_id}", tags=["rating"])


@router.put("/rating", status_code=status.HTTP_204_NO_CONTENT)
def rate_movie(
        movie_id: int,
        movie_rating: MovieRatingCreate,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
):
    movie = get_movie_by_id(session, movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Filme não encontrado")

    create_or_update_rating(session, movie_id, current_user.id, movie_rating.rating)
    return current_user


@router.delete("/rating", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie_rating(
        movie_id: int,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
):
    if get_movie_by_id(session, movie_id) is None:
        raise HTTPException(status_code=404, detail="Filme não encontrado")

    movie_rating = get_rating_by_id_and_user(session, movie_id, current_user.id)

    if movie_rating is None:
        raise HTTPException(status_code=400, detail="Usuario não avaliou esse filme")

    delete_rating(session, movie_rating)


@router.get("/ratings", status_code=status.HTTP_200_OK)
def get_movie_rating(
        movie_id: int,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
):
    if get_movie_by_id(session, movie_id) is None:
        raise HTTPException(status_code=404, detail="Filme não encontrado")

    return get_movie_rating_summary(session, movie_id)
