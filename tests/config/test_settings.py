"""Test configuration settings module."""
import pytest
from av_studio.config.settings import Settings, ModelProvider


def test_settings_default():
    """Test default settings values."""
    settings = Settings()
    assert settings.app_name == "AV Studio"
    assert settings.debug is False
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000


def test_model_provider_enum():
    """Test ModelProvider enum values."""
    assert ModelProvider.OLLAMA == "ollama"
    assert ModelProvider.MLX == "mlx"
    assert ModelProvider.OPENAI == "openai"
    assert ModelProvider.ANTHROPIC == "anthropic"
    assert ModelProvider.GOOGLE == "google"


def test_settings_paths_exist():
    """Test that configured paths are created."""
    settings = Settings()
    assert settings.base_dir.exists()
    assert settings.media_dir.exists()
    assert settings.models_dir.exists()
    assert settings.cache_dir.exists()
