from pinecone import Pinecone
from pinecone_plugins.assistant.models.chat import Message

# Initialize Pinecone and get the assistant
import os
import time
import json
from pinecone import Pinecone
from django.conf import settings

# Load Django settings to access environment variables
try:
    from django.conf import settings
    api_key = settings.PINECONE_API_KEY
except:
    # Fallback to direct environment variable access
    api_key = os.getenv('PINECONE_API_KEY', '')

if not api_key:
    raise ValueError("PINECONE_API_KEY environment variable is required")

pc = Pinecone(api_key=api_key)

assistant = pc.assistant.Assistant(
    assistant_name="example-assistant", 
)

# Create a message and get response
msg = Message(content="Are positive, negative, or neutral sentiments more common in posts?")
resp = assistant.chat(messages=[msg])

print(resp)