#!/usr/bin/env python3
"""
Quick test to verify OpenAI API key
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

openai_key = os.getenv('OPENAI_API_KEY', '')
print(f"OpenAI API Key found: {'Yes' if openai_key else 'No'}")
print(f"Key starts with sk-: {openai_key.startswith('sk-') if openai_key else False}")
print(f"Key length: {len(openai_key)}")

if openai_key:
    print(f"First 10 chars: {openai_key[:10]}...")
    print(f"Last 10 chars: ...{openai_key[-10:]}")
else:
    print("No API key found!")

# Test OpenAI client initialization
try:
    import openai
    client = openai.OpenAI(api_key=openai_key)
    print("OpenAI client initialized successfully")
    
    # Try a simple completion to test the key
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        print(f"API test successful: {response.choices[0].message.content}")
    except Exception as e:
        print(f"API call failed: {e}")
        
except Exception as e:
    print(f"Failed to initialize OpenAI client: {e}")