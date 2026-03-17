from typing import Annotated, Callable

from fastapi import Depends

from app.types.service import BaseSessionService
from app.web.dependencies.database import DatabaseSessionDep


def get_session_service[T: BaseSessionService](cls: type[T]) -> Callable[[DatabaseSessionDep], T]:
    def service_dependency(session: DatabaseSessionDep) -> T:
        return cls(session=session)

    return service_dependency


# type SomeServiceDep = Annotated[SomeService, Depends(get_session_service(SomeService))]
