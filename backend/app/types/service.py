from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    pass


class BaseSessionService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
