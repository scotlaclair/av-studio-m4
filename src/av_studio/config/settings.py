"""
Central configuration using Pydantic Settings for type safety and validation.
"""

from enum import Enum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class ModelProvider(str, Enum):
    OLLAMA = "ollama"
    MLX = "mlx"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    app_name: str = "AV Studio"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Paths
    base_dir: Path = Path.home() / "av-studio"
    media_dir: Path = Field(default_factory=lambda: Path.home() / "av-studio" / "media")
    models_dir: Path = Field(default_factory=lambda: Path.home() / "av-studio" / "models")
    cache_dir: Path = Field(default_factory=lambda: Path.home() / "av-studio" / "cache")

    # Local LLM - Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_default_model: str = "llama3.2:8b"

    # Local LLM - MLX (recommended for M4 Max)
    mlx_default_model: str = "mlx-community/Llama-3.2-8B-Instruct-4bit"
    mlx_max_tokens: int = 4096

    # External APIs
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    elevenlabs_api_key: str | None = None

    # Processing
    use_mps: bool = True  # Metal Performance Shaders
    use_mlx: bool = True  # Apple MLX framework
    max_concurrent_jobs: int = 4

    # Smart Router defaults
    default_local_model: str = "ollama"
    cost_threshold_usd: float = 0.10  # Route to local if cost exceeds
    latency_threshold_ms: int = 500  # Route to local if latency exceeds

    # Database
    database_url: str = "sqlite:///./av_studio.db"

    # Redis (optional, for caching)
    redis_url: str | None = "redis://localhost:6379"

    class Config:
        env_file = ".env"
        env_prefix = "AV_"


settings = Settings()

# Ensure directories exist
for dir_path in [settings.base_dir, settings.media_dir, settings.models_dir, settings.cache_dir]:
    dir_path.mkdir(parents=True, exist_ok=True)
