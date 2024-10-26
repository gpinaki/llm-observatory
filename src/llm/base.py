# src/llm/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import time
import uuid
from datetime import datetime
from src.config.settings import settings

class LLMException(Exception):
    """
    Custom exception for LLM-related errors.
    Used to provide clear error messages for LLM-specific issues.
    
    Examples:
        >>> raise LLMException("API key is invalid")
        >>> raise LLMException("Model not supported")
    """
    pass

class BaseLLM(ABC):
    """
    Abstract base class for Large Language Model implementations.
    
    This class defines the interface that all LLM providers (like OpenAI, Anthropic)
    must implement. It provides common functionality and tracking capabilities.
    
    Attributes:
        api_key (str): Authentication key for the LLM provider
        model (Optional[str]): Name of the specific model to use
        session_id (str): Unique identifier for the current session
        application_id (str): Identifier for the application using the LLM
        environment (str): Environment where the LLM is running (e.g., 'dev', 'prod')
        logger (logging.Logger): Logger instance for this class
        created_at (datetime): Timestamp when the instance was created
        
    Usage:
        class OpenAILLM(BaseLLM):
            def setup(self):
                # Implementation
                pass
    """
    
    def __init__(self, 
                 api_key: str, 
                 model: Optional[str] = None,
                 application_id: Optional[str] = None,
                 environment: str = "development"):
        """
        Initialize the LLM instance with tracking capabilities.
        
        Args:
            api_key (str): Authentication key for the LLM provider
            model (Optional[str]): Specific model to use. If None, a default will be used
            application_id (Optional[str]): Identifier for the calling application
            environment (str): Runtime environment (development/staging/production)
            
        Raises:
            LLMException: If api_key is empty or invalid
            
        Example:
            >>> llm = OpenAILLM(
            ...     api_key="sk-...",
            ...     model="gpt-4",
            ...     application_id="web-app-1",
            ...     environment="production"
            ... )
        """
        # Store initialization parameters
        self.api_key = api_key
        self.model = model
        
        # Generate and store tracking identifiers
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
        
        # Validate API key
        if not api_key:
            self.logger.error("API key not provided")
            raise LLMException("API key is required")
            
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
        
        This method should:
        1. Initialize the API client
        2. Validate the model selection
        3. Set up any provider-specific configurations
        
        Raises:
            LLMException: If setup fails
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
        
        Args:
            prompt (str): The input text to send to the LLM
            temperature (float): Controls randomness in generation (0.0 to 1.0)
            max_tokens (int): Maximum number of tokens to generate
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - response (str): The generated text
                - metadata (dict): Additional information including:
                    - tokens (dict): Token usage statistics
                    - model (str): Model used
                    - response_time (float): Time taken to generate
                    - finish_reason (str): Why the generation stopped
                    - session_info (dict): Session and tracking information
        """
        pass
        
    def log_interaction(self, prompt: str, response: Dict[str, Any]) -> None:
        """
        Log details of an LLM interaction with enhanced tracking.
        
        Args:
            prompt (str): The input prompt
            response (Dict[str, Any]): The complete response dictionary
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
        
        Args:
            response (Dict[str, Any]): Response dictionary to validate
            
        Returns:
            bool: True if response is valid, False otherwise
        """
        required_keys = {"response", "metadata"}
        return all(key in response for key in required_keys)
        
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get current session information and metrics.
        
        Returns:
            Dict[str, Any]: Session information including:
                - session_id: Unique session identifier
                - application_id: Application identifier
                - environment: Runtime environment
                - created_at: Session creation timestamp
                - metrics: Usage metrics for the session
                
        Example:
            >>> session_info = llm.get_session_info()
            >>> print(f"Total cost for session: ${session_info['metrics']['total_cost']}")
        """
        return {
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
        
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Return information about the current model configuration.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - provider (str): Name of the LLM provider
                - model (str): Current model name
                - supported_models (List[str]): Available models
                - max_tokens (int): Maximum token limit
                - cost_per_token (Dict): Token cost information
                - session_info (Dict): Current session information
        """
        pass