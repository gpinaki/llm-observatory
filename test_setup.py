# test_setup.py

from src.config.settings import settings
import os
from pathlib import Path

def verify_directory_structure():
    """Verify if all required directories exist and are accessible."""
    required_dirs = {
        "Base Directory": settings.BASE_DIR,
        "Logs Directory": settings.LOG_DIR,
        "Data Directory": settings.DATA_DIR
    }
    
    print("\nDirectory Structure Check:")
    print("-" * 50)
    for name, path in required_dirs.items():
        exists = Path(path).exists()
        status = "✅" if exists else "❌"
        print(f"{name}: {path} {status}")
        if not exists:
            try:
                Path(path).mkdir(parents=True, exist_ok=True)
                print(f"  → Created {name}")
            except Exception as e:
                print(f"  → Error creating directory: {str(e)}")

def verify_config_values():
    """Verify configuration values are loaded correctly."""
    print("\nConfiguration Values:")
    print("-" * 50)
    print(f"Project Name: {settings.PROJECT_NAME}")
    print(f"Version: {settings.VERSION}")
    print(f"Debug Mode: {settings.DEBUG}")

def verify_api_keys():
    """Verify API keys are available."""
    print("\nAPI Keys Status:")
    print("-" * 50)
    key_status = settings.validate_api_keys()
    for provider, is_valid in key_status.items():
        status = "✅ Available" if is_valid else "❌ Missing"
        print(f"{provider.upper()} API Key: {status}")

def verify_model_configurations():
    """Verify model configurations."""
    print("\nModel Configurations:")
    print("-" * 50)
    
    print("OpenAI Models:")
    for model in settings.LLM.OPENAI_MODELS:
        print(f"  • {model}")
        cost = settings.get_model_cost("openai", model)
        if cost:
            print(f"    - Input cost: ${cost.get('input', 'N/A')}/1K tokens")
            print(f"    - Output cost: ${cost.get('output', 'N/A')}/1K tokens")
    
    print("\nAnthropic Models:")
    for model in settings.LLM.ANTHROPIC_MODELS:
        print(f"  • {model}")
        cost = settings.get_model_cost("anthropic", model)
        if cost:
            print(f"    - Input cost: ${cost.get('input', 'N/A')}/1K tokens")
            print(f"    - Output cost: ${cost.get('output', 'N/A')}/1K tokens")

def verify_monitoring_config():
    """Verify monitoring configuration."""
    print("\nMonitoring Configuration:")
    print("-" * 50)
    print("Metrics being tracked:")
    for metric in settings.MONITORING.METRICS_TO_TRACK:
        print(f"  • {metric}")
    
    print("\nAlert Thresholds:")
    for metric, threshold in settings.MONITORING.ALERT_THRESHOLDS.items():
        print(f"  • {metric}: {threshold}")

def main():
    """Run all verification checks."""
    print("\n=== LLM Observatory Configuration Verification ===")
    
    try:
        verify_directory_structure()
        verify_config_values()
        verify_api_keys()
        verify_model_configurations()
        verify_monitoring_config()
        
        print("\n✅ Configuration verification completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during verification: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Ensure .env file exists with required API keys")
        print("2. Verify directory permissions")
        print("3. Check PYTHONPATH includes project root")
        print(f"Current PYTHONPATH: {os.getenv('PYTHONPATH', 'Not set')}")

if __name__ == "__main__":
    main()