from datetime import datetime, timedelta

from sqlmodel import Session, select

from app.models import PasswordResetToken


def create_recovery_token(session: Session, user_id: int, token: str):
    reset_token = PasswordResetToken(
        user_id=user_id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(minutes=30)
    )

    session.add(reset_token)
    session.commit()


def get_reset_by_token(session: Session, token: str) -> PasswordResetToken | None:
    return session.exec(select(PasswordResetToken).where(PasswordResetToken.token == token)).first()


def use_recovery_token(session: Session, password_reset_token: PasswordResetToken):
    password_reset_token.used = True

    session.add(password_reset_token)
    session.commit()
