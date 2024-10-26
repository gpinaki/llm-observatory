# test_setup.py
import streamlit as st
import openai
import anthropic
from dotenv import load_dotenv
import os

def test_imports():
    print("✓ All imports successful")

def test_env():
    load_dotenv()
    keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY']
    for key in keys:
        value = os.getenv(key)
        if value:
            masked_key = value[:4] + '*' * (len(value) - 8) + value[-4:]
            print(f"✓ {key} found: {masked_key}")
        else:
            print(f"✗ {key} not found")

if __name__ == "__main__":
    print("Running setup verification...")
    test_imports()
    test_env()