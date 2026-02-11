"""
CORS middleware configuration for ROGER - Valeria API
"""

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from app.config.settings import settings


def setup_cors(app: FastAPI) -> None:
    """
    Setup CORS middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )
