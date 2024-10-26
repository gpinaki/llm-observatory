# tests/test_llm/test_openai.py

import pytest
from src.llm.openai_llm import OpenAILLM
from src.config.settings import settings

@pytest.mark.asyncio
class TestOpenAILLM:
    """Test suite for OpenAI LLM implementation."""
    
    @pytest.fixture(autouse=True)
    async def setup_and_teardown(self):
        """Setup and teardown for each test."""
        # Setup
        self.llm = OpenAILLM(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-3.5-turbo",
            application_id="test-suite",
            environment="testing"
        )
        
        yield
        
        # Teardown - cleanup any async resources
        if hasattr(self.llm, 'client'):
            await self.llm.client.close()
    
    async def test_openai_initialization(self):
        """Test basic OpenAI LLM initialization."""
        assert self.llm.model == "gpt-3.5-turbo"
        assert self.llm.application_id == "test-suite"
        assert self.llm.environment == "testing"
        
        # Verify API key validation
        key_status = settings.check_api_keys()
        assert isinstance(key_status, dict)
    
    async def test_model_info(self):
        """Test model info retrieval."""
        info = self.llm.get_model_info()
        assert info["provider"] == "OpenAI"
        assert info["model"] == "gpt-3.5-turbo"
        assert "capabilities" in info
        assert "cost_info" in info