"""
Settings module for ROGER - Valeria API
Uses Pydantic Settings for configuration management
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # ===================================
    # APPLICATION
    # ===================================
    app_name: str = Field(default="ROGER - Valeria API", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    # ===================================
    # AI CONFIGURATION
    # ===================================
    use_local_embeddings: bool = Field(default=True, alias="USE_LOCAL_EMBEDDINGS")
    use_local_object_detection: bool = Field(default=True, alias="USE_LOCAL_OBJECT_DETECTION")
    
    # ===================================
    # API
    # ===================================
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    api_title: str = Field(default="ROGER API", alias="API_TITLE")
    api_version: str = Field(default="0.1.0", alias="API_VERSION")
    cors_origins: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        alias="CORS_ORIGINS"
    )
    
    # ===================================
    # DATABASE
    # ===================================
    database_url: str = Field(
        default="sqlite+aiosqlite:///./valeria.db",
        alias="DATABASE_URL"
    )
    
    # ===================================
    # AUTHENTICATION & JWT
    # ===================================
    secret_key: str = Field(
        default="your-super-secret-key-change-in-production",
        alias="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    jwt_access_token_expire_minutes: int = Field(
        default=30,
        alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = Field(
        default=7,
        alias="REFRESH_TOKEN_EXPIRE_DAYS"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7,
        alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )
    
    # ===================================
    # OPENAI
    # ===================================
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        alias="OPENAI_EMBEDDING_MODEL"
    )
    openai_max_tokens: int = Field(default=1000, alias="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, alias="OPENAI_TEMPERATURE")
    
    # ===================================
    # ANTHROPIC (optional)
    # ===================================
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: Optional[str] = Field(
        default="claude-3-5-sonnet-20241022",
        alias="ANTHROPIC_MODEL"
    )
    
    # ===================================
    # VECTOR DATABASE
    # ===================================
    chroma_persist_directory: str = Field(
        default="./chroma_db",
        alias="CHROMA_PERSIST_DIRECTORY"
    )
    chroma_collection_name: str = Field(
        default="roger_images",
        alias="CHROMA_COLLECTION_NAME"
    )
    qdrant_url: Optional[str] = Field(default=None, alias="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(default=None, alias="QDRANT_API_KEY")
    
    # ===================================
    # CACHE (Redis)
    # ===================================
    redis_enabled: bool = Field(default=False, alias="REDIS_ENABLED")
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    redis_expire_time: int = Field(default=3600, alias="REDIS_EXPIRE_TIME")
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        alias="REDIS_URL"
    )
    redis_cache_ttl: int = Field(default=3600, alias="REDIS_CACHE_TTL")
    
    # ===================================
    # STORAGE
    # ===================================
    storage_type: str = Field(default="local", alias="STORAGE_TYPE")
    storage_path: str = Field(default="./storage/images", alias="STORAGE_PATH")
    upload_dir: str = Field(default="./uploads", alias="UPLOAD_DIR")
    max_upload_size: int = Field(default=10485760, alias="MAX_UPLOAD_SIZE")  # 10MB
    allowed_extensions: str = Field(
        default="jpg,jpeg,png,gif,webp,tiff",
        alias="ALLOWED_EXTENSIONS"
    )
    aws_access_key_id: Optional[str] = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(
        default=None,
        alias="AWS_SECRET_ACCESS_KEY"
    )
    s3_bucket_name: Optional[str] = Field(default=None, alias="S3_BUCKET_NAME")
    
    # ===================================
    # RATE LIMITING
    # ===================================
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_per_minute: int = Field(
        default=60,
        alias="RATE_LIMIT_PER_MINUTE"
    )
    
    # ===================================
    # LOGGING
    # ===================================
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")
    log_file: str = Field(default="./logs/app.log", alias="LOG_FILE")

    # ===================================
    # PAGINATION
    # ===================================
    default_page_size: int = Field(default=20, alias="DEFAULT_PAGE_SIZE")
    max_page_size: int = Field(default=100, alias="MAX_PAGE_SIZE")
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"


# Global settings instance
settings = Settings()


