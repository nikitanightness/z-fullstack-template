from fastapi import APIRouter

from app.web.routes import common, v1

# Root APIRouter
router = APIRouter()

# Include common APIRouter (handles '/' and '/health' endpoints)
router.include_router(common.router)

# Include /v1 APIRouter
router.include_router(v1.router)
