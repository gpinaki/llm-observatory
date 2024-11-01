# tests/test_config/test_settings.py

import pytest
from pathlib import Path
from src.config.settings import Settings, LLMConfig, MonitoringConfig

@pytest.fixture
def settings():
    """Create settings instance for testing."""
    return Settings()

def test_settings_initialization(settings):
    """Test if settings are properly initialized."""
    assert settings.PROJECT_NAME == "LLM Observatory"
    assert isinstance(settings.VERSION, str)
    assert isinstance(settings.BASE_DIR, Path)

def test_llm_config(settings):
    """Test LLM configuration."""
    assert isinstance(settings.LLM.OPENAI_MODELS, list)
    assert isinstance(settings.LLM.ANTHROPIC_MODELS, list)
    assert "gpt-4" in settings.LLM.OPENAI_MODELS
    assert "claude-3-haiku-20240307" in settings.LLM.ANTHROPIC_MODELS

def test_monitoring_config(settings):
    """Test monitoring configuration."""
    assert isinstance(settings.MONITORING.METRICS_TO_TRACK, list)
    assert "response_time" in settings.MONITORING.METRICS_TO_TRACK
    assert isinstance(settings.MONITORING.ALERT_THRESHOLDS, dict)

def test_api_key_validation(settings):
    """Test API key validation."""
    validation_result = settings.validate_keys()
    assert isinstance(validation_result, dict)
    assert "openai" in validation_result
    assert "anthropic" in validation_result

def test_cost_tracking(settings):
    """Test cost tracking functionality."""
    gpt4_cost = settings.get_model_cost("openai", "gpt-4")
    assert isinstance(gpt4_cost, dict)
    assert "input" in gpt4_cost
    assert "output" in gpt4_cost

def test_directory_setup(settings, tmp_path):
    """Test directory creation."""
    settings.BASE_DIR = tmp_path
    settings.LOG_DIR = tmp_path / "logs"
    settings.DATA_DIR = tmp_path / "data"
    
    settings.setup_directories()
    assert settings.LOG_DIR.exists()
    assert settings.DATA_DIR.exists()