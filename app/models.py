from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import EmailStr, ConfigDict, BaseModel
from sqlmodel import SQLModel, Field, CheckConstraint


class MovieStatus(str, Enum):
    suggestion = "suggestion"
    watchlist = "watchlist"
    watched = "watched"


class Token(SQLModel):
    access_token: str
    token_type: str


class UserBase(SQLModel):
    username: str = Field(index=True, min_length=2, max_length=30)
    email: EmailStr = Field(unique=True, index=True)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    password: str | None = Field(min_length=6)
    created_at: datetime | None = Field(default_factory=datetime.utcnow, nullable=False)


class UserCreate(UserBase):
    model_config = ConfigDict(extra="forbid")
    password: str = Field(min_length=6)
    invite_code: str


class UserPublic(UserBase):
    id: int
    created_at: datetime


class MovieBase(SQLModel):
    tmdb_id: int
    title: str
    poster_url: str


class Movie(MovieBase, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    status: MovieStatus
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    added_by: int | None = Field(default=None, foreign_key="user.id")


class MovieCreate(MovieBase):
    model_config = ConfigDict(extra="forbid")


class MoviePublic(MovieBase):
    id: int
    status: MovieStatus
    created_at: datetime
    added_by: int


class MovieInterestBase(SQLModel):
    user_id: int = Field(default=None, foreign_key="user.id")
    movie_id: int = Field(default=None, foreign_key="movie.id")


class MovieInterest(MovieInterestBase, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)


class MovieRatingBase(SQLModel):
    user_id: int = Field(default=None, foreign_key="user.id")
    movie_id: int = Field(default=None, foreign_key="movie.id")
    rating: int = Field(ge=1, le=10)


class MovieRating(MovieRatingBase, table=True):
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )

    id: int | None = Field(default=None, primary_key=True, index=True)
    rated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class MovieRatingCreate(MovieRatingBase):
    model_config = ConfigDict(extra="forbid")


class FilterParams(BaseModel):
    page_size: int = Field(100, gt=0, le=100)
    page: int = Field(0, ge=0)
    order_by: str
    order_direction: Literal["asc", "desc"] = "desc"

    def validate_order_by(self, model) -> bool:
        return self.order_by in model.__fields__
