from logging import getLogger
from typing import Annotated, AsyncGenerator

from fastapi import Depends, FastAPI, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app import config
from app.database.wrapper import DatabaseWrapper

logger = getLogger(__name__)


async def startup_database(app: FastAPI) -> None:
    logger.info("Initializing database...")
    app.state.database = DatabaseWrapper(url=config.database.db_url)


async def shutdown_database(app: FastAPI) -> None:
    database: DatabaseWrapper = app.state.database

    logger.info("Disposing database engine...")
    await database.dispose()


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    db: DatabaseWrapper = request.app.state.database

    async with db.session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


type DatabaseSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
