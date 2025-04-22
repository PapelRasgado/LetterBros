from typing import Sequence
from sqlmodel import select, Session, desc

from app.models import Movie, MovieCreate, FilterParams, MovieStatus


def get_movie_by_tmdb(session: Session, tmdb_id: int) -> Movie | None:
    return session.exec(select(Movie).where(Movie.tmdb_id == tmdb_id)).first()


def get_movie_by_id(session: Session, movie_id: int) -> Movie | None:
    return session.exec(select(Movie).where(Movie.id == movie_id)).first()


def get_movies(session: Session, movie_status: MovieStatus, filter_p: FilterParams) -> Sequence[Movie]:
    return session.exec(
        select(Movie)
        .where(Movie.status == movie_status.value)
        .limit(filter_p.page_size)
        .offset(filter_p.page_size * filter_p.page)
        .order_by(desc(filter_p.order_by) if filter_p.order_direction == "desc" else filter_p.order_by)
    ).all()


def save_movie(session: Session, movie: Movie) -> Movie:
    session.add(movie)
    session.commit()
    session.refresh(movie)

    return movie



def create_movie(session: Session, movie: MovieCreate, user_id: int) -> Movie:
    movie_data = movie.model_dump()
    movie_data["status"] = MovieStatus.suggestion
    movie_data["added_by"] = user_id

    movie_db = Movie.model_validate(movie_data)

    session.add(movie_db)
    session.commit()
    session.refresh(movie_db)

    return movie_db
