"""
Main FastAPI Application
Entry point for the IoT Smart Home Agent Platform backend.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from backend.api.config import get_settings
from backend.api.dependencies import lifespan_manager
from backend.api.routes import router
from backend.api.websocket import websocket_endpoint

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        get_settings().log_level.value
    ),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    settings = get_settings()
    logger.info(
        "application_startup",
        app_name=settings.app_name,
        version=settings.app_version,
        iot_mode=settings.iot_mode,
    )
    
    async with lifespan_manager(settings):
        yield
    
    logger.info("application_shutdown")


# Create FastAPI app
app = FastAPI(
    title="IoT Smart Home Agent Platform",
    version="1.0.0",
    description="Enterprise voice-controlled IoT platform with Clean Architecture",
    lifespan=lifespan,
)

# CORS middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1", tags=["IoT Control"])

# WebSocket endpoint
app.add_websocket_route("/ws/telemetry", websocket_endpoint)


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "websocket": "/ws/telemetry",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled errors."""
    logger.error("unhandled_exception", error=str(exc), path=str(request.url))
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.value.lower(),
    )
