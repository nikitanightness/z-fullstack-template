import orjson
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import Response
from fastapi.utils import is_body_allowed_for_status_code
from starlette.exceptions import HTTPException as StarletteHTTPException


# TODO: Refactor this!
# Note: fastapi.responses.ORJSONResponse is now deprecated, because FastAPI now uses
# pydantic_core serializer (but only for response_models, which not supported by exception_handlers)
# Refs: https://github.com/fastapi/fastapi/pull/14964, https://github.com/fastapi/fastapi/pull/14962
def serialize_json(obj: dict) -> bytes:
    return orjson.dumps(obj)


async def custom_request_validation_error_handler(
    _request: Request,
    exc: RequestValidationError,
) -> Response:
    return Response(
        status_code=422,
        content=serialize_json({"detail": exc.errors()}),
    )


async def custom_http_exception_handler(
    _request: Request,
    exc: StarletteHTTPException,
) -> Response:
    headers = getattr(exc, "headers", None)

    if not is_body_allowed_for_status_code(exc.status_code):
        return Response(
            status_code=exc.status_code,
            headers=headers,
        )

    return Response(
        status_code=exc.status_code,
        headers=headers,
        content=serialize_json({"error": exc.detail}),
    )


async def custom_internal_server_error_handler(
    _request: Request,
    _exc: Exception,
) -> Response:
    return Response(
        status_code=500,
        content=serialize_json({"error": "Internal Server Error"}),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, custom_http_exception_handler)
    app.add_exception_handler(RequestValidationError, custom_request_validation_error_handler)

    # This handler will be overridden by built-in 'Starlette Debugger' when DEBUG mode enabled.
    app.add_exception_handler(500, custom_internal_server_error_handler)
