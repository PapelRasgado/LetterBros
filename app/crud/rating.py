from sqlalchemy import func
from sqlmodel import Session, select

from app.models import MovieRating, MovieRatingSummary


def create_or_update_rating(session: Session, movie_id: int, user_id: int, movie_rating: int):
    movie_rating_db = session.exec(
        select(MovieRating).where(
            MovieRating.movie_id == movie_id,
            MovieRating.user_id == user_id
        )
    ).first()

    if movie_rating_db is None:
        movie_rating_db = MovieRating(
            movie_id=movie_id,
            user_id=user_id
        )

    movie_rating_db.rating = movie_rating

    session.add(movie_rating_db)
    session.commit()


def get_rating_by_id_and_user(session: Session, movie_id: int, user_id: int) -> MovieRating | None:
    return session.exec(select(MovieRating).where(MovieRating.movie_id == movie_id, MovieRating.user_id == user_id)).first()


def delete_rating(session: Session, movie_rating: MovieRating):
    session.delete(movie_rating)
    session.commit()


def get_movie_rating_summary(session: Session, movie_id: int) -> MovieRatingSummary:
    result = session.exec(
        select(
            func.count(MovieRating.id),
            func.avg(MovieRating.rating)
        ).where(MovieRating.movie_id == movie_id)
    ).first()

    count, average = result
    return MovieRatingSummary(
        rating_count=count if count else None,
        rating_average=round(average, 1) if average is not None else None
    )
