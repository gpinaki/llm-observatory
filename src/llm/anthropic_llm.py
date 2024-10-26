# src/llm/anthropic_llm.py

from typing import Dict, Any, Optional
from anthropic import AsyncAnthropic, APIError
import time
import asyncio
from datetime import datetime
from src.llm.base import BaseLLM, LLMException
from src.config.settings import settings

class AnthropicLLM(BaseLLM):
    """
    Anthropic LLM implementation with async support and comprehensive tracking.
    
    This class implements the BaseLLM interface for Anthropic's API, providing:
    - Async API interactions
    - Cost tracking
    - Performance monitoring
    - Error handling
    - Resource management
    """
    
    def setup(self) -> None:
        """Initialize and configure the Anthropic client."""
        try:
            # Initialize async client
            self.client = AsyncAnthropic(
                api_key=self.api_key
            )
            
            # Set default model if none provided
            self.model = self.model or "claude-3-haiku-20240307"
            
            # Validate model selection
            if self.model not in settings.LLM.ANTHROPIC_MODELS:
                raise LLMException(
                    f"Invalid model: {self.model}. "
                    f"Choose from {settings.LLM.ANTHROPIC_MODELS}"
                )
            
            self.logger.info(
                f"Anthropic client initialized [Session: {self.session_id}] "
                f"[Model: {self.model}] [Environment: {self.environment}]"
            )
                
        except Exception as e:
            error_msg = f"Failed to initialize Anthropic client: {str(e)}"
            self.logger.error(f"{error_msg} [Session: {self.session_id}]")
            raise LLMException(error_msg)
    
    async def cleanup(self) -> None:
        """Cleanup resources and close connections."""
        try:
            if hasattr(self, 'client'):
                await self.client.close()
                self.logger.info(f"Cleaned up Anthropic client [Session: {self.session_id}]")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)} [Session: {self.session_id}]")
            
    async def generate_response(self,
                              prompt: str,
                              temperature: float = settings.LLM.DEFAULT_PARAMETERS["temperature"],
                              max_tokens: int = settings.LLM.DEFAULT_PARAMETERS["max_tokens"],
                              **kwargs) -> Dict[str, Any]:
        """Generate a response using Anthropic's API."""
        try:
            start_time = time.time()
            
            # Make API call with retry logic
            for attempt in range(settings.LLM.DEFAULT_PARAMETERS["retry_attempts"]):
                try:
                    response = await self.client.messages.create(
                        model=self.model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        **kwargs
                    )
                    break
                except APIError as e:
                    if attempt == settings.LLM.DEFAULT_PARAMETERS["retry_attempts"] - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Calculate costs
            model_costs = settings.get_model_cost("anthropic", self.model)
            input_cost = (response.usage.input_tokens / 1000) * model_costs["input"]
            output_cost = (response.usage.output_tokens / 1000) * model_costs["output"]
            total_cost = input_cost + output_cost
            
            result = {
                "response": response.content[0].text,
                "metadata": {
                    "model": self.model,
                    "tokens": {
                        "prompt_tokens": response.usage.input_tokens,
                        "completion_tokens": response.usage.output_tokens,
                        "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                    },
                    "costs": {
                        "input_cost": round(input_cost, 6),
                        "output_cost": round(output_cost, 6),
                        "total_cost": round(total_cost, 6)
                    },
                    "performance": {
                        "response_time": round(response_time, 3),
                        "tokens_per_second": round(
                            (response.usage.input_tokens + response.usage.output_tokens) / response_time, 
                            2
                        ),
                        "retry_count": attempt
                    },
                    "session_info": self.get_session_info(),
                    "completion_info": {
                        "stop_reason": response.stop_reason,
                        "created": datetime.now().isoformat()
                    }
                }
            }
            
            if not self.validate_response(result):
                raise LLMException("Invalid response format from Anthropic")
            
            self.log_interaction(prompt, result)
            return result
            
        except APIError as e:
            error_msg = f"Anthropic API error: {str(e)}"
            self.logger.error(f"{error_msg} [Session: {self.session_id}]")
            raise LLMException(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(f"{error_msg} [Session: {self.session_id}]")
            raise LLMException(error_msg)
            
    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive model information."""
        model_costs = settings.get_model_cost("anthropic", self.model)
        
        return {
            "provider": "Anthropic",
            "model": self.model,
            "capabilities": {
                "max_tokens": settings.LLM.DEFAULT_PARAMETERS["max_tokens"],
                "supported_models": settings.LLM.ANTHROPIC_MODELS,
            },
            "cost_info": {
                "input_cost": model_costs.get("input", 0),
                "output_cost": model_costs.get("output", 0)
            },
            "session_info": self.get_session_info(),
            "default_parameters": settings.LLM.DEFAULT_PARAMETERS
        }