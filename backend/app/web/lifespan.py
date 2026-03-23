from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI

from app.web.dependencies.database import shutdown_database, startup_database


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    # Startup Actions
    await startup_database(app)

    yield

    # Shutdown Actions
    await shutdown_database(app)
