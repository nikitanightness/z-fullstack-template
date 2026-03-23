from fastapi import APIRouter

from app import config

router = APIRouter(include_in_schema=False)


@router.get("/")
async def root() -> dict:
    return {
        "name": config.app.name,
        "display_name": config.app.display_name,
        "version": config.app.version,
    }


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}
