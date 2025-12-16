"""
Configuration Management - Environment Variables & Settings
"""
from enum import Enum
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """
    
    # Application
    app_name: str = "IoT Smart Home Agent Platform"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: LogLevel = LogLevel.INFO
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["*"]
    
    # Hardware
    iot_mode: str = Field(default="AUTO", pattern="^(AUTO|ARDUINO|SIMULATION)$")
    serial_port: str | None = None
    baud_rate: int = 9600
    
    # OpenAI (Optional - required only for voice commands)
    openai_api_key: str = Field(default="sk-dummy-key-for-testing-only-replace-in-production")
    openai_model: str = "gpt-4o-mini"
    
    # Telemetry
    telemetry_broadcast_interval: float = 1.0  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Application settings
    """
    return Settings()
