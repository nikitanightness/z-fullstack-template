from typing import TypedDict

from app.database.wrapper import DatabaseWrapper


class AppState(TypedDict):
    db: DatabaseWrapper
