# src/config/settings.py

# Standard library imports
import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Third-party imports
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LogConfig:
    """Logging configuration."""
    FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LEVEL: str = "INFO"
    FILENAME: str = "llm_observatory.log"

class LLMConfig:
    """LLM-specific configurations."""
    OPENAI_MODELS: List[str] = [
        "gpt-4-turbo-preview",
        "gpt-4",
        "gpt-3.5-turbo"
    ]
    
    ANTHROPIC_MODELS: List[str] = [
        "claude-3-5-sonnet-latest",
        "claude-3-opus-latest",
        "claude-3-haiku-20240307"
    ]
    GEMINI_MODELS: List[str] = [
        "gemini-1",
        "gemini-2"
    ]
    DEFAULT_PARAMETERS: Dict[str, Any] = {
        "temperature": 0.7,
        "max_tokens": 500,
        "timeout": 30,  # seconds
        "retry_attempts": 3
    }

class MonitoringConfig:
    """Monitoring-specific configurations."""
    METRICS_TO_TRACK: List[str] = [
        "response_time",
        "token_usage",
        "cost",
        "error_rate"
    ]
    
    ALERT_THRESHOLDS: Dict[str, float] = {
        "response_time": 5.0,  # seconds
        "error_rate": 0.1,     # 10%
        "cost_limit": 10.0     # dollars
    }

class Settings(BaseSettings):
    """Main configuration class."""
    
    # Project metadata
    PROJECT_NAME: str = "LLM Observatory"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # File paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    LOG_DIR: Path = BASE_DIR / "logs"
    DATA_DIR: Path = BASE_DIR / "data"
    
    # Configurations
    LLM: LLMConfig = LLMConfig()
    LOGGING: LogConfig = LogConfig()
    MONITORING: MonitoringConfig = MonitoringConfig()
    
    # Cost tracking
    MODEL_COSTS: Dict[str, Dict[str, Dict[str, float]]] = {
        "openai": {
            "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
        },
        "anthropic": {
            "claude-3-5-sonnet-latest": {"input": 0.003, "output": 0.015},
            "claude-3-opus-latest": {"input": 0.015, "output": 0.075},
            "claude-3-haiku-20240307": {"input": 0.015, "output": 0.075}
        }
    }
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @field_validator("OPENAI_API_KEY", "ANTHROPIC_API_KEY", mode="before")
    def validate_keys(cls, v: str, info: Field) -> str:
        """Validate API keys from environment."""
        if not v:
            v = os.getenv(info.name, "")
        return v
    
    def setup_logging(self) -> None:
        """Setup logging configuration."""
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, self.LOGGING.LEVEL),
            format=self.LOGGING.FORMAT,
            handlers=[
                logging.FileHandler(self.LOG_DIR / self.LOGGING.FILENAME),
                logging.StreamHandler()
            ]
        )
    
    def setup_directories(self) -> None:
        """Create necessary directories."""
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    def check_api_keys(self) -> Dict[str, bool]:
        """Check if API keys are present."""
        return {
            "openai": bool(self.OPENAI_API_KEY),
            "anthropic": bool(self.ANTHROPIC_API_KEY)
        }
    
    def get_model_cost(self, provider: str, model: str) -> Dict[str, float]:
        """Get cost per token for a specific model."""
        return self.MODEL_COSTS.get(provider, {}).get(model, {})

# Create settings instance
settings = Settings()

# Setup logging and directories
settings.setup_directories()
settings.setup_logging()

logger = logging.getLogger(__name__)
logger.info(f"Loaded configuration for {settings.PROJECT_NAME} v{settings.VERSION}")