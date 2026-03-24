from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.web.dependencies.database import setup_database, shutdown_database
from app.web.state import AppState


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncIterator[AppState]:
    state: AppState | dict = {}  # FIXME: Perhaps temporarily, consider other solutions

    # Startup Actions
    await setup_database(state)

    yield state

    # Shutdown Actions
    await shutdown_database(state)
