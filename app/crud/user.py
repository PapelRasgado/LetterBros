from sqlmodel import select, Session

from app.models import User, UserCreate


def get_user_by_email_or_username(session: Session, email: str, username: str) -> User | None:
    return session.exec(select(User).where(User.email == email or User.username == username)).first()


def get_user_by_username(session: Session, username: str) -> User | None:
    return session.exec(select(User).where(User.username == username)).first()


def get_user_by_id(session: Session, user_id: int) -> User | None:
    return session.exec(select(User).where(User.id == user_id)).first()


def create_user(session: Session, user: UserCreate) -> User:
    user_db = User.model_validate(user)

    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db
