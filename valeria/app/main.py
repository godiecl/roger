"""
ROGER - Valeria API
Main FastAPI application entry point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import structlog

from app.config.settings import settings
from app.infrastructure.database.session import init_db, close_db
from app.infrastructure.middleware.cors import setup_cors
from app.infrastructure.cache.redis_cache import cache

# Import routers
from app.features.authenticate.interfaces.api.routes import router as auth_router
from app.features.view_images.interfaces.api.routes import router as images_router
from app.features.search_filter.interfaces.api.routes import router as search_router
from app.features.generate_narrative.interfaces.api.routes import router as narratives_router

# Setup logging
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting ROGER - Valeria API", version=settings.app_version)
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Connect to Redis cache
    try:
        await cache.connect()
        logger.info("Redis cache connected")
    except Exception as e:
        logger.warning("Redis cache connection failed", error=str(e))
    
    yield
    
    # Shutdown
    logger.info("Shutting down ROGER - Valeria API")
    
    # Close database connections
    await close_db()
    logger.info("Database connections closed")
    
    # Disconnect from Redis
    try:
        await cache.disconnect()
        logger.info("Redis cache disconnected")
    except Exception:
        pass


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Plataforma Tecnológica para la Visibilización de Colecciones Patrimoniales",
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    lifespan=lifespan
)

# Setup CORS
setup_cors(app)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Plataforma Tecnológica para la Visibilización de Colecciones Patrimoniales",
        "docs": f"{settings.api_prefix}/docs",
        "health": "/health"
    }

# Include routers
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(images_router, prefix=settings.api_prefix)
app.include_router(search_router, prefix=settings.api_prefix)
app.include_router(narratives_router, prefix=settings.api_prefix)

# Serve static files (images, uploads)
# app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unexpected errors."""
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error": str(exc),
                "type": type(exc).__name__
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
