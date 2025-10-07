from LinkedInHandler import LinkedInPineconeDB, load_linkedin_posts_from_file

# Initialize
import os
from LinkedInHandler import LinkedInPineconeDB
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

db = LinkedInPineconeDB(api_key=api_key, index_name="linkedin-db")
db.create_index()

# Load and upload posts
posts = load_linkedin_posts_from_file("../Sample Data/LinkedIn posts.json")
db.upload_posts(posts)

# Search posts
results = db.search_posts("family business management", top_k=5)