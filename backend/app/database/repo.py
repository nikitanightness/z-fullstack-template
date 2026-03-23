import logging
from functools import cached_property
from typing import Any, get_args, overload
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import ColumnExpressionArgument, Select, func, literal, select
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.model import BaseSQLAModel


def apply_select_params(
    query: Select,
    *expr_filters: ColumnExpressionArgument[bool],
    limit: int = None,
    offset: int = None,
    order_by: tuple[str | ColumnExpressionArgument[Any]] = None,  # noqa; FIXME: Type hint (IntelliJ bug?)
    **kwargs_filters: Any,  # noqa: ANN401
) -> Select:

    if expr_filters:
        query = query.filter(*expr_filters)

    if kwargs_filters:
        query = query.filter_by(**kwargs_filters)

    if order_by:
        first_clause, *extra_clauses = order_by
        query = query.order_by(first_clause, *extra_clauses)

    if limit:
        query = query.limit(limit)

    if offset:
        query = query.offset(offset)

    return query


class BaseRepository[M: BaseSQLAModel, PK: (int, str, UUID)]:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._logger = logging.getLogger()

    @cached_property
    def model_class(
        self,
    ) -> type[M]:
        orig_bases = getattr(self, "__orig_bases__")

        # If repo class has many bases,
        # then BaseRepository MUST be at the end bases list.
        # e.g.: ItemRepository(
        #     BaseClass1,
        #     BaseClass2,
        #     BaseRepository[SomeModel, int]
        # )
        repo_base = orig_bases[-1]

        model_type, _ = get_args(repo_base)
        return model_type

    async def create(
        self,
        instance: M,
    ) -> M:
        """
        Persist a new entity instance to the database.
        """

        try:
            self._session.add(instance)

            await self._session.flush()
            await self._session.refresh(instance)

            return instance
        except SQLAlchemyError as e:
            await self._session.rollback()

            self._logger.error(f"Failed to create '{self.model_class.__name__}'", exc_info=True)

            raise e

    async def get(
        self,
        pk: PK,
    ) -> M | None:
        """
        Retrieve an entity by its primary key.
        """

        return await self._session.get(self.model_class, pk)

    async def find_one(
        self,
        *expr_filters: ColumnExpressionArgument[bool],
        **kwargs_filters: Any,  # noqa: ANN401
    ) -> M | None:
        """
        Retrieve the first entity that matches the filters.
        """

        query = apply_select_params(select(self.model_class), *expr_filters, limit=2, **kwargs_filters)
        result = await self._session.scalars(query)

        return result.one_or_none()  # Will raise exception if found more than one object

    async def find(
        self,
        *expr_filters: ColumnExpressionArgument[bool],
        limit: int | None = None,
        offset: int | None = None,
        order_by: tuple[str | ColumnExpressionArgument[Any]] = None,  # noqa; FIXME: Type hint (IntelliJ bug?)
        **kwargs_filters: Any,  # noqa: ANN401
    ) -> list[M]:
        """
        Retrieve entities that match the filters.
        Supports pagination.
        """

        query = apply_select_params(
            select(self.model_class),
            *expr_filters,
            limit=limit,
            offset=offset,
            order_by=order_by,
            **kwargs_filters,
        )
        result = await self._session.scalars(query)

        return list(result.all())

    @overload
    async def update(
        self,
        pk: PK,
        model_or_fields: BaseModel,
    ) -> M: ...

    @overload
    async def update(
        self,
        pk: PK,
        model_or_fields: BaseModel,
        **fields: Any,  # noqa: ANN401
    ) -> M: ...

    @overload
    async def update(
        self,
        pk: PK,
        model_or_fields: dict[str, Any],
    ) -> M: ...

    @overload
    async def update(
        self,
        pk: PK,
        model_or_fields: dict[str, Any],
        **fields: Any,  # noqa: ANN401
    ) -> M: ...

    @overload
    async def update(
        self,
        pk: PK,
        **fields: Any,  # noqa: ANN401
    ) -> M: ...

    async def update(
        self,
        pk: PK,
        model_or_fields: BaseModel | dict[str, Any] = None,
        **fields: Any,  # noqa: ANN401
    ) -> M:
        """Update an existing entity's fields."""

        update_data: dict[str, Any] = {}

        # Check that data is present
        if model_or_fields is None and not fields:
            raise ValueError(
                "Expected at least one argument (pydantic.BaseModel, dict[str, Any], "
                "or fields passed directly via kwargs), but got none."
            )

        # Dump to dict if it's a 'pydantic.BaseModel'
        if isinstance(model_or_fields, BaseModel):
            update_data = model_or_fields.model_dump(exclude_unset=True)

        # If it's a dict, just copy data
        elif isinstance(model_or_fields, dict):
            update_data = model_or_fields.copy()

        # Throw error if type is invalid
        elif model_or_fields is not None:
            raise TypeError(
                "Invalid type! Expected 'pydantic.BaseModel' or 'dict[str, Any]', "
                f"but received '{type(model_or_fields).__name__}'."
            )

        # Add or override fields from kwargs (fields)
        update_data |= fields

        db_obj = await self.get(pk)
        if not db_obj:
            raise NoResultFound()

        try:
            # Update fields
            for key, value in update_data.items():
                # Warn if db_obj doesn't have requested field
                if not hasattr(db_obj, key):
                    self._logger.warning(
                        "Tried to change value of undefined field of '%s' model: %s (value: %s)",
                        db_obj.__class__.__name__,
                        key,
                        str(value),
                    )
                    continue

                # Set new value
                setattr(db_obj, key, value)

            await self._session.flush()
            await self._session.refresh(db_obj)

            return db_obj
        except SQLAlchemyError as e:
            await self._session.rollback()

            self._logger.error(f"Failed to update '{self.model_class.__name__}' with PK: {pk}", exc_info=True)

            raise e

    async def delete(
        self,
        pk: PK,
    ) -> None:
        """
        Remove an entity from the database by its primary key.
        """

        db_obj = await self.get(pk)
        if not db_obj:
            raise NoResultFound()

        try:
            await self._session.delete(db_obj)
            await self._session.flush()
        except SQLAlchemyError as e:
            await self._session.rollback()

            self._logger.error(f"Failed to delete '{self.model_class.__name__}' with PK: {pk}", exc_info=True)

            raise e

    async def count(
        self,
        *expr_filters: ColumnExpressionArgument[bool],
        **kwargs_filters: Any,  # noqa: ANN401
    ) -> int:
        """
        Count the total number of entities matching the filters.
        """

        query = apply_select_params(
            select(func.count()).select_from(self.model_class),
            *expr_filters,
            **kwargs_filters,
        )
        result = await self._session.execute(query)

        return result.scalar() or 0

    async def exists(
        self,
        *expr_filters: ColumnExpressionArgument[bool],
        **kwargs_filters: Any,  # noqa: ANN401
    ) -> bool:
        """
        Check if an entity exists.
        """

        query = (
            apply_select_params(
                select(literal(1)).select_from(self.model_class),
                *expr_filters,
                **kwargs_filters,
            )
            .exists()
            .select()
        )
        result = await self._session.execute(query)

        return bool(result.scalar())
