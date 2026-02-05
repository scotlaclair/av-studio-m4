"""Pytest configuration and fixtures."""
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def test_data_dir():
    """Return path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def temp_audio_file(tmp_path):
    """Create a temporary audio file for testing."""
    audio_file = tmp_path / "test_audio.wav"
    audio_file.touch()
    return audio_file


@pytest.fixture
def mock_env(monkeypatch):
    """Set up mock environment variables."""
    monkeypatch.setenv("AV_DEBUG", "true")
    monkeypatch.setenv("AV_OPENAI_API_KEY", "test_key")
    monkeypatch.setenv("AV_ANTHROPIC_API_KEY", "test_key")
