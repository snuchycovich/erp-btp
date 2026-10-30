"""FastAPI application exposing quote management."""

from fastapi import FastAPI

from app.infrastructure.persistence.database import Base, engine
from app.presentation.api.routes.quotes import router as quotes_router

app = FastAPI(title="BTP Project Manager")


# Pour l'exercice uniquement.
# Les migrations seront ensuite gérées avec Alembic.
Base.metadata.create_all(bind=engine)

app.include_router(quotes_router)
