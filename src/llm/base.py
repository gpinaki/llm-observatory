from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import uuid
from datetime import datetime
from src.config.settings import settings
import os

class LLMException(Exception):
    """
    Custom exception for LLM-related errors.
    Used to provide clear error messages for LLM-specific issues.
    """

class BaseLLM(ABC):
    """
    Abstract base class for Large Language Model implementations.
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None,  # Made optional for ADC
                 model: Optional[str] = None,
                 application_id: Optional[str] = None,
                 environment: str = "development"):
        """
        Initialize the LLM instance with tracking capabilities.
        
        Args:
            api_key (Optional[str]): Authentication key for the LLM provider, if required
            model (Optional[str]): Specific model to use. If None, a default will be used
            application_id (Optional[str]): Identifier for the calling application
            environment (str): Runtime environment (development/staging/production)
            
        Raises:
            LLMException: If neither API key nor GOOGLE_APPLICATION_CREDENTIALS is provided
        """
        # Determine authentication method
        self.api_key = api_key
        self.use_adc = bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

        # Raise an exception if neither ADC nor API key is provided
        if not self.use_adc and not self.api_key:
            raise LLMException("Either GOOGLE_APPLICATION_CREDENTIALS or an API key is required for authentication.")

        # Store other initialization parameters
        self.model = model
        self.session_id = str(uuid.uuid4())
        self.application_id = application_id or "default-app"
        self.environment = environment
        self.created_at = datetime.now()

        # Initialize interaction tracking
        self.total_requests = 0
        self.total_tokens = 0
        self.total_cost = 0.0

        # Set up logging with context
        self.logger = logging.getLogger(f"{__name__}.{self.session_id}")
        self.logger.debug(
            f"Initializing {self.__class__.__name__} "
            f"[Session: {self.session_id}, App: {self.application_id}, Env: {self.environment}]"
        )
        
        # Initialize the LLM
        try:
            self.setup()
        except Exception as e:
            self.logger.error(f"Setup failed: {str(e)}")
            raise
    
    @abstractmethod
    def setup(self) -> None:
        """
        Set up the LLM client and configuration.
        """
        pass
        
    @abstractmethod
    async def generate_response(self, 
                            prompt: str,
                            temperature: float = settings.LLM.DEFAULT_PARAMETERS["temperature"],
                            max_tokens: int = settings.LLM.DEFAULT_PARAMETERS["max_tokens"],
                            **kwargs) -> Dict[str, Any]:
        """
        Generate a response from the LLM.
        """
        pass

    def log_interaction(self, prompt: str, response: Dict[str, Any]) -> None:
        """
        Log details of an LLM interaction with enhanced tracking.
        """
        try:
            # Update tracking metrics
            self.total_requests += 1
            self.total_tokens += response.get('metadata', {}).get('tokens', {}).get('total_tokens', 0)
            self.total_cost += response.get('metadata', {}).get('costs', {}).get('total_cost', 0.0)
            
            # Create timestamp for the log
            timestamp = datetime.now().isoformat()
            
            # Prepare interaction details with tracking information
            interaction = {
                "timestamp": timestamp,
                "session_id": self.session_id,
                "application_id": self.application_id,
                "environment": self.environment,
                "model": self.model,
                "prompt": prompt,
                "response": response,
                "cumulative_metrics": {
                    "total_requests": self.total_requests,
                    "total_tokens": self.total_tokens,
                    "total_cost": self.total_cost
                }
            }
            
            # Log the interaction
            self.logger.info(f"Interaction logged: {interaction}")
            
        except Exception as e:
            self.logger.error(f"Error logging interaction: {str(e)}")
            
    def validate_response(self, response: Dict[str, Any]) -> bool:
        """
        Validate the structure of an LLM response.
        """
        required_keys = {"response", "metadata"}
        return all(key in response for key in required_keys)
        
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get current session information and metrics.
        """
        import json
        session_info = {
            "session_id": self.session_id,
            "application_id": self.application_id,
            "environment": self.environment,
            "created_at": self.created_at.isoformat(),
            "metrics": {
                "total_requests": self.total_requests,
                "total_tokens": self.total_tokens,
                "total_cost": self.total_cost
            }
        }
        return json.dumps(session_info, indent=4)
        
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Return information about the current model configuration.
        """
        pass
