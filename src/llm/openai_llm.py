# src/llm/openai_llm.py

from typing import Dict, Any, Optional
from openai import AsyncOpenAI, OpenAIError
import time
import asyncio
from datetime import datetime
from src.llm.base import BaseLLM, LLMException
from src.config.settings import settings

class OpenAILLM(BaseLLM):
    """
    OpenAI LLM implementation with async support and comprehensive tracking.
    
    This class implements the BaseLLM interface for OpenAI's API, providing:
    - Async API interactions
    - Cost tracking
    - Performance monitoring
    - Error handling
    - Resource management
    
    Attributes:
        api_key (str): OpenAI API key
        model (str): Selected OpenAI model
        client (AsyncOpenAI): Async OpenAI client instance
        session_id (str): Unique session identifier
        application_id (str): Application identifier
        environment (str): Runtime environment
    """
    
    def setup(self) -> None:
        """
        Initialize and configure the OpenAI client.
        
        Validates model selection and sets up API client with proper configuration.
        
        Raises:
            LLMException: If initialization fails or model is invalid
        """
        try:
            # Initialize async client
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                timeout=settings.LLM.DEFAULT_PARAMETERS["timeout"]
            )
            
            # Set default model if none provided
            self.model = self.model or "gpt-3.5-turbo"
            
            # Validate model selection
            if self.model not in settings.LLM.OPENAI_MODELS:
                raise LLMException(
                    f"Invalid model: {self.model}. "
                    f"Choose from {settings.LLM.OPENAI_MODELS}"
                )
            
            self.logger.info(
                f"OpenAI client initialized [Session: {self.session_id}] "
                f"[Model: {self.model}] [Environment: {self.environment}]"
            )
                
        except Exception as e:
            error_msg = f"Failed to initialize OpenAI client: {str(e)}"
            self.logger.error(f"{error_msg} [Session: {self.session_id}]")
            raise LLMException(error_msg)
    
    async def cleanup(self) -> None:
        """
        Cleanup resources and close connections.
        Should be called when the LLM instance is no longer needed.
        """
        try:
            if hasattr(self, 'client'):
                await self.client.close()
                self.logger.info(f"Cleaned up OpenAI client [Session: {self.session_id}]")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)} [Session: {self.session_id}]")
            
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        await self.cleanup()
            
    async def generate_response(self,
                              prompt: str,
                              temperature: float = settings.LLM.DEFAULT_PARAMETERS["temperature"],
                              max_tokens: int = settings.LLM.DEFAULT_PARAMETERS["max_tokens"],
                              **kwargs) -> Dict[str, Any]:
        """
        Generate a response using OpenAI's API with comprehensive tracking.
        
        Args:
            prompt (str): Input text for the model
            temperature (float): Controls randomness (0.0 to 1.0)
            max_tokens (int): Maximum tokens to generate
            **kwargs: Additional OpenAI-specific parameters
            
        Returns:
            Dict[str, Any]: Response dictionary containing:
                - response (str): Generated text
                - metadata (dict): Comprehensive metadata including:
                    - model: Model used
                    - tokens: Token usage statistics
                    - costs: Cost breakdown
                    - performance: Response time metrics
                    - session_info: Session tracking data
                    
        Raises:
            LLMException: For API errors or unexpected issues
        """
        try:
            # Record start time
            start_time = time.time()
            
            # Prepare request parameters
            request_params = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }
            
            # Make API call with retry logic
            for attempt in range(settings.LLM.DEFAULT_PARAMETERS["retry_attempts"]):
                try:
                    response = await self.client.chat.completions.create(**request_params)
                    break
                except OpenAIError as e:
                    if attempt == settings.LLM.DEFAULT_PARAMETERS["retry_attempts"] - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
            # Calculate timing and costs
            end_time = time.time()
            response_time = end_time - start_time
            
            # Get cost information
            model_costs = settings.get_model_cost("openai", self.model)
            prompt_cost = (response.usage.prompt_tokens / 1000) * model_costs["input"]
            completion_cost = (response.usage.completion_tokens / 1000) * model_costs["output"]
            total_cost = prompt_cost + completion_cost
            
            # Prepare comprehensive response
            result = {
                "response": response.choices[0].message.content,
                "metadata": {
                    "model": self.model,
                    "tokens": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "costs": {
                        "prompt_cost": round(prompt_cost, 6),
                        "completion_cost": round(completion_cost, 6),
                        "total_cost": round(total_cost, 6)
                    },
                    "performance": {
                        "response_time": round(response_time, 3),
                        "tokens_per_second": round(response.usage.total_tokens / response_time, 2),
                        "retry_count": attempt
                    },
                    "session_info": self.get_session_info(),
                    "completion_info": {
                        "finish_reason": response.choices[0].finish_reason,
                        "created": datetime.fromtimestamp(response.created).isoformat()
                    }
                }
            }
            
            # Validate response format
            if not self.validate_response(result):
                raise LLMException("Invalid response format from OpenAI")
            
            # Log interaction
            self.log_interaction(prompt, result)
            
            return result
            
        except OpenAIError as e:
            error_msg = f"OpenAI API error: {str(e)}"
            self.logger.error(f"{error_msg} [Session: {self.session_id}]")
            raise LLMException(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(f"{error_msg} [Session: {self.session_id}]")
            raise LLMException(error_msg)
            
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get comprehensive model information.
        
        Returns:
            Dict[str, Any]: Model information including:
                - provider: OpenAI
                - model: Current model name
                - capabilities: Model capabilities and limits
                - cost_info: Token cost information
                - session_info: Current session data
                - default_parameters: Default configuration
        """
        model_costs = settings.get_model_cost("openai", self.model)
        
        return {
            "provider": "OpenAI",
            "model": self.model,
            "capabilities": {
                "max_tokens": settings.LLM.DEFAULT_PARAMETERS["max_tokens"],
                "supported_models": settings.LLM.OPENAI_MODELS,
            },
            "cost_info": {
                "input_cost": model_costs.get("input", 0),
                "output_cost": model_costs.get("output", 0)
            },
            "session_info": self.get_session_info(),
            "default_parameters": settings.LLM.DEFAULT_PARAMETERS
        }