from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import users, movies, auth, interest, rating

app = FastAPI()

app.include_router(users.router)
app.include_router(movies.router)
app.include_router(auth.router)
app.include_router(interest.router)
app.include_router(rating.router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

