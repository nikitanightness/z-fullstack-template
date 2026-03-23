from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.web.lifespan import app_lifespan
from app.web.routes import router as root_router


def build_app() -> FastAPI:
    """
    ASGI App Factory
    """

    app = FastAPI(
        # Info
        debug=config.debug,
        title=config.app.display_name,
        version=config.app.version,
        # Docs
        docs_url="/docs" if config.app.enable_docs else None,
        redoc_url="/redoc" if config.app.enable_docs else None,
        openapi_url="/openapi.json" if config.app.enable_docs else None,
        # Other
        redirect_slashes=True,
        lifespan=app_lifespan,
    )

    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.security.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include root APIRouter
    app.include_router(root_router)

    return app
