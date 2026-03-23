from datetime import datetime
from typing import Annotated

from pydantic import PlainSerializer

type Timestamp = Annotated[
    datetime,
    PlainSerializer(
        lambda dt: int(dt.timestamp()),
        return_type=int,
    ),
]
