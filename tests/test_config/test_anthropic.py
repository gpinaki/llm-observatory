# test_anthropic_minimal.py
import os
from anthropic import Anthropic
from dotenv import load_dotenv

def check_api_setup():
    """Check API setup without making an actual API call."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get API key
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("❌ ANTHROPIC_API_KEY not found in .env file")
            return False
            
        # Initialize Anthropic client
        client = Anthropic(api_key=api_key)
        
        print("\n✅ Anthropic client initialized successfully")
        print("\nAvailable Models:")
        print("-" * 50)
        print("1. claude-3-haiku-20240307 (Fastest, most cost-effective)")
        print("2. claude-3-sonnet-20240307 (Balanced)")
        print("3. claude-3-opus-20240307 (Most capable)")
        print("\nPricing Information:")
        print("-" * 50)
        print("Haiku: $0.25/million input tokens, $0.75/million output tokens")
        print("Sonnet: $3/million input tokens, $15/million output tokens")
        print("Opus: $15/million input tokens, $75/million output tokens")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error checking Anthropic setup: {str(e)}")
        return False

def print_setup_instructions():
    """Print instructions for setting up Anthropic billing."""
    print("\nTo set up Anthropic billing:")
    print("-" * 50)
    print("1. Go to https://console.anthropic.com/")
    print("2. Click on 'Billing' or 'Plans & Billing'")
    print("3. Add a payment method")
    print("4. Purchase credits")
    print("\nRecommended for testing:")
    print("- Start with a small amount ($10-$20)")
    print("- Use the claude-3-haiku model for initial testing")
    print("- Monitor usage in the console")

if __name__ == "__main__":
    print("\nChecking Anthropic API setup...")
    if check_api_setup():
        print_setup_instructions()
