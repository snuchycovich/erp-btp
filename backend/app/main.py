"""FastAPI application exposing quote management."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.persistence.database import Base, engine
from app.presentation.api.routes.quotes import router as quotes_router

app = FastAPI(title="BTP Project Manager")


# Pour l'exercice uniquement.
# Les migrations seront ensuite gérées avec Alembic.
Base.metadata.create_all(bind=engine)

app.include_router(quotes_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)
