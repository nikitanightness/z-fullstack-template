from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

METADATA = MetaData()


class BaseSQLAModel(DeclarativeBase):
    metadata = METADATA
