from typing import Any

from pydantic import BaseModel, model_serializer
from pydantic.fields import FieldInfo
from pydantic_core.core_schema import SerializerFunctionWrapHandler

__all__ = ["SortOrder", "BaseSchema"]

"""
Example:

class Item(BaseSchema):
    name: str

class ItemOut(ItemBase):
    id: int
    created_at: Timestamp

JSON-serialized ItemOut: {"name": "...", "id": 0, "created_at": "..."}

class ItemOut2(ItemBase):
    id: Annotated[int, SortOrder(-50)]
    created_at: Annotated[Timestamp, SortOrder(50)]

JSON-serialized ItemOut2: {"id": 0, "name": "...", "created_at": "..."}
"""

DEFAULT_ORDER_VALUE = 0


class SortOrder:
    def __init__(self, order: int = DEFAULT_ORDER_VALUE) -> None:
        self.order = order


def extract_field_weight(field_info: FieldInfo, default: int = DEFAULT_ORDER_VALUE) -> int:
    for meta in field_info.metadata:
        if isinstance(meta, SortOrder):
            return meta.order
    return default


class BaseSchema(BaseModel):
    @model_serializer(mode="wrap")
    def _serialize_sort_ordered_model(self, handler: SerializerFunctionWrapHandler) -> Any:  # noqa: ANN401
        result = handler(self)

        if not isinstance(result, dict):
            return result

        weights = {name: extract_field_weight(field_info) for name, field_info in self.model_fields.items()}
        return dict(
            sorted(
                result.items(),
                key=lambda item: weights.get(item[0], 0),
            ),
        )
