# test_openai.py
import os
from openai import OpenAI
from dotenv import load_dotenv

def check_openai_setup():
    """Check OpenAI API setup and make a test call."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY not found in .env file")
            return False
            
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        print("\n✅ OpenAI client initialized successfully")
        
        # Make a minimal test call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hi! Please respond with: 'OpenAI connection successful'"}
            ],
            max_tokens=20
        )
        
        print("\nTest API Call Result:")
        print("-" * 50)
        print(f"Response: {response.choices[0].message.content}")
        print(f"Model: {response.model}")
        print(f"Usage - Total Tokens: {response.usage.total_tokens}")
        
        print("\nAvailable Models:")
        print("-" * 50)
        print("1. GPT-4 Models:")
        print("   - gpt-4-turbo-preview (Latest)")
        print("   - gpt-4 (Standard)")
        
        print("\n2. GPT-3.5 Models:")
        print("   - gpt-3.5-turbo (Latest)")
        print("   - gpt-3.5-turbo-16k (Extended context)")
        
        print("\nPricing Information (per 1K tokens):")
        print("-" * 50)
        print("GPT-4 Turbo:")
        print("- Input: $0.01")
        print("- Output: $0.03")
        
        print("\nGPT-4:")
        print("- Input: $0.03")
        print("- Output: $0.06")
        
        print("\nGPT-3.5 Turbo:")
        print("- Input: $0.0005")
        print("- Output: $0.0015")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing OpenAI API: {str(e)}")
        print("\nCommon solutions:")
        print("1. Check if your API key is correct")
        print("2. Verify your API key has been activated")
        print("3. Check if you have sufficient API credits")
        print("4. Verify your internet connection")
        return False

def print_cost_saving_tips():
    """Print tips for cost-effective API usage."""
    print("\nCost Saving Tips:")
    print("-" * 50)
    print("1. Use GPT-3.5-Turbo for development/testing")
    print("   - It's ~60x cheaper than GPT-4")
    print("   - Suitable for most testing scenarios")
    
    print("\n2. Optimize token usage:")
    print("   - Use shorter prompts")
    print("   - Set appropriate max_tokens")
    print("   - Clear conversation history when not needed")
    
    print("\n3. Monitor usage:")
    print("   - Set up usage limits in OpenAI dashboard")
    print("   - Track token usage in your application")
    print("   - Review usage patterns regularly")

def check_remaining_credits():
    """Print instructions for checking OpenAI credits."""
    print("\nTo check OpenAI credits and usage:")
    print("-" * 50)
    print("1. Go to https://platform.openai.com/")
    print("2. Click on 'Settings' -> 'Billing'")
    print("3. View your usage and remaining credits")
    print("4. Set up usage limits if needed")

if __name__ == "__main__":
    print("\nTesting OpenAI API connection...")
    if check_openai_setup():
        print_cost_saving_tips()
        check_remaining_credits()