from logging import getLogger
from typing import Annotated, AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app import config
from app.database.wrapper import DatabaseWrapper
from app.web.state import AppState

logger = getLogger(__name__)


async def setup_database(state: dict) -> None:
    logger.info("Initializing database...")

    state |= {
        "db": DatabaseWrapper(url=config.database.db_url),
    }


async def shutdown_database(state: AppState) -> None:
    db = state["db"]

    logger.info("Disposing database engine...")
    await db.dispose()


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    state: AppState = request.app.state

    db = state["db"]
    async with db.session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


type DatabaseSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
