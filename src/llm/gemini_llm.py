from typing import Dict, Any, Optional
import vertexai
from vertexai.preview.generative_models import GenerativeModel
import time
import asyncio
from datetime import datetime
from src.llm.base import BaseLLM, LLMException
from src.config.settings import settings
import os

class GeminiLLM(BaseLLM):
    """
    Gemini LLM implementation using Vertex AI.
    """
    
    def setup(self) -> None:
        """Initialize and configure the Gemini client."""
        try:
            # Ensure GOOGLE_APPLICATION_CREDENTIALS is set for ADC
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
            if not credentials_path:
                raise LLMException("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")
            
            # Initialize Vertex AI with ADC
            vertexai.init(
                project=settings.GOOGLE_CLOUD_PROJECT,
                location=settings.GOOGLE_CLOUD_LOCATION
            )
            
            # Set default model if none provided
            self.model = self.model or "gemini-1.0-pro"
            
            # Validate model selection
            if self.model not in settings.LLM.GEMINI_MODELS:
                raise LLMException(
                    f"Invalid model: {self.model}. "
                    f"Choose from {settings.LLM.GEMINI_MODELS}"
                )
            
            # Initialize the model
            self.client = GenerativeModel(self.model)
            
            self.logger.info(
                f"Gemini client initialized [Session: {self.session_id}] "
                f"[Model: {self.model}] [Environment: {self.environment}]"
            )
                
        except Exception as e:
            error_msg = f"Failed to initialize Gemini client: {str(e)}"
            self.logger.error(f"{error_msg} [Session: {self.session_id}]")
            raise LLMException(error_msg)
    
    async def generate_response(self,
                                prompt: str,
                                temperature: float = settings.LLM.DEFAULT_PARAMETERS["temperature"],
                                max_tokens: int = settings.LLM.DEFAULT_PARAMETERS["max_tokens"],
                                **kwargs) -> Dict[str, Any]:
        """Generate a response using Gemini's API."""
        try:
            start_time = time.time()
            
            # Make API call with retry logic
            for attempt in range(settings.LLM.DEFAULT_PARAMETERS["retry_attempts"]):
                try:
                    response = await asyncio.to_thread(
                        self.client.generate_content,
                        prompt,
                        generation_config={
                            "temperature": temperature,
                            "max_output_tokens": max_tokens,
                            **kwargs
                        }
                    )
                    break
                except Exception as e:
                    if attempt == settings.LLM.DEFAULT_PARAMETERS["retry_attempts"] - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Calculate tokens (Gemini provides characters, estimating tokens)
            prompt_chars = len(prompt)
            response_chars = len(response.text)
            estimated_prompt_tokens = prompt_chars // 4  # Rough estimation
            estimated_completion_tokens = response_chars // 4
            
            # Calculate costs (update with actual Gemini pricing)
            model_costs = settings.get_model_cost("gemini", self.model)
            input_cost = (estimated_prompt_tokens / 1000) * model_costs["input"]
            output_cost = (estimated_completion_tokens / 1000) * model_costs["output"]
            total_cost = input_cost + output_cost
            
            result = {
                "response": response.text,
                "metadata": {
                    "model": self.model,
                    "tokens": {
                        "prompt_tokens": estimated_prompt_tokens,
                        "completion_tokens": estimated_completion_tokens,
                        "total_tokens": estimated_prompt_tokens + estimated_completion_tokens
                    },
                    "costs": {
                        "input_cost": round(input_cost, 6),
                        "output_cost": round(output_cost, 6),
                        "total_cost": round(total_cost, 6)
                    },
                    "performance": {
                        "response_time": round(response_time, 3),
                        "tokens_per_second": round(
                            (estimated_prompt_tokens + estimated_completion_tokens) / response_time, 
                            2
                        ),
                        "retry_count": attempt
                    },
                    "session_info": self.get_session_info(),
                    "completion_info": {
                        "stop_reason": "stop",  # Gemini doesn't provide this directly
                        "created": datetime.now().isoformat()
                    }
                }
            }
            
            if not self.validate_response(result):
                raise LLMException("Invalid response format from Gemini")
            
            self.log_interaction(prompt, result)
            return result
            
        except Exception as e:
            error_msg = f"Gemini API error: {str(e)}"
            self.logger.error(f"{error_msg} [Session: {self.session_id}]")
            raise LLMException(error_msg)
            
    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive model information."""
        model_costs = settings.get_model_cost("gemini", self.model)
        
        return {
            "provider": "Gemini",
            "model": self.model,
            "capabilities": {
                "max_tokens": settings.LLM.DEFAULT_PARAMETERS["max_tokens"],
                "supported_models": settings.LLM.GEMINI_MODELS,
            },
            "cost_info": {
                "input_cost": model_costs.get("input", 0),
                "output_cost": model_costs.get("output", 0)
            },
            "session_info": self.get_session_info(),
            "default_parameters": settings.LLM.DEFAULT_PARAMETERS
        }
