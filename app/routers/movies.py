from typing import Annotated, Sequence

from fastapi import APIRouter, status, Depends, HTTPException, Query
from sqlmodel import Session

from app.auth import get_current_user
from app.crud.movie import get_movie_by_tmdb, get_movies, get_movie_by_id, save_movie, create_movie
from app.database import get_session
from app.models import User, MoviePublic, MovieCreate, MovieStatus, FilterParams

router = APIRouter(prefix="/movies", tags=["movies"])


@router.post("", response_model=MoviePublic, status_code=status.HTTP_201_CREATED)
def suggest_movie(
        movie: MovieCreate,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Session = Depends(get_session)
):
    if get_movie_by_tmdb(session, movie.tmdb_id):
        raise HTTPException(status_code=400, detail="Filme já cadastrado")

    movie_db = create_movie(session, movie, current_user.id)

    return movie_db


@router.get("/{movie_status}", response_model=Sequence[MoviePublic], status_code=status.HTTP_200_OK)
def list_movies(
        movie_status: MovieStatus,
        filter_query: Annotated[FilterParams, Query()],
        current_user: Annotated[User, Depends(get_current_user)],
        session: Session = Depends(get_session)
):
    if not filter_query.validate_order_by(MoviePublic):
        raise HTTPException(status_code=400, detail=f"Campo inválido para ordenação: {filter_query.order_by}")

    movie_db = get_movies(session, movie_status, filter_query)

    return movie_db


@router.post("/{movie_id}/status/{movie_status}", status_code=status.HTTP_204_NO_CONTENT)
def update_movies_status(
        movie_id: int,
        movie_status: MovieStatus,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Session = Depends(get_session)
):
    movie = get_movie_by_id(session, movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Filme não encontrado")

    movie.status = movie_status.value
    save_movie(session, movie)