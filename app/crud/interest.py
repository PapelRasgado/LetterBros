from typing import Sequence

from sqlmodel import select, Session

from app.models import MovieInterest, User


def get_interest_by_id_and_user(session: Session, movie_id: int, user_id: int) -> MovieInterest | None:
    return session.exec(select(MovieInterest).where(MovieInterest.movie_id == movie_id and MovieInterest.user_id == user_id)).first()


def get_users_by_movie_interest(session: Session, movie_id: int) -> Sequence[User]:
    return session.exec(select(User).join(MovieInterest).where(MovieInterest.movie_id == movie_id)).all()


def delete_interest(session: Session, movie_interest: MovieInterest):
    session.delete(movie_interest)
    session.commit()


def create_interest(session: Session, movie_interest: MovieInterest):
    session.add(movie_interest)
    session.commit()
