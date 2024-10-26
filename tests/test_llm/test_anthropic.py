# tests/test_llm/test_anthropic.py

import pytest
from src.llm.anthropic_llm import AnthropicLLM
from src.config.settings import settings

@pytest.mark.asyncio
class TestAnthropicLLM:
    """Test suite for Anthropic LLM implementation."""
    
    @pytest.fixture(autouse=True)
    async def setup_and_teardown(self):
        """Setup and teardown for each test."""
        self.llm = AnthropicLLM(
            api_key=settings.ANTHROPIC_API_KEY,
            model="claude-3-haiku-20240307",
            application_id="test-suite",
            environment="testing"
        )
        
        yield
        
        await self.llm.cleanup()
    
    async def test_anthropic_initialization(self):
        """Test basic Anthropic LLM initialization."""
        assert self.llm.model == "claude-3-haiku-20240307"
        assert self.llm.application_id == "test-suite"
        assert self.llm.environment == "testing"
        
        key_status = settings.check_api_keys()
        assert isinstance(key_status, dict)
        assert "anthropic" in key_status
    
    async def test_model_info(self):
        """Test model info retrieval."""
        info = self.llm.get_model_info()
        assert info["provider"] == "Anthropic"
        assert info["model"] == "claude-3-haiku-20240307"
        assert "capabilities" in info
        assert "cost_info" in info