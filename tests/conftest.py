import pytest
from src.config.settings import settings

@pytest.fixture(scope="session")
def test_settings():
    """Provide test settings."""
    return settings

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Setup test environment."""
    monkeypatch.setenv("ENVIRONMENT", "testing")
    return None