import os
import sys
import django

# Add the parent directory to the sys.path to find the Django project
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

import sqlite3
from django.db import connection

# First, let's make sure we're using the correct database
db_path = connection.settings_dict['NAME']
print(f"Using database at: {db_path}")

# Connect to SQLite database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get current table schema
c.execute("PRAGMA table_info(facebook_data_facebookpost)")
columns = {col[1]: col for col in c.fetchall()}
print(f"Found {len(columns)} columns in the table")

# Define missing columns and their types
missing_columns = {
    'followers': 'INTEGER NULL',
    'user_posted': 'VARCHAR(100) NULL',
    'description': 'TEXT NULL',
    'content': 'TEXT NULL',
    'content_type': 'VARCHAR(50) NULL',
    'hashtags': 'TEXT NULL',
    'likes': 'INTEGER DEFAULT 0',
    'count_reactions_type': 'TEXT NULL',
    'num_likes_type': 'TEXT NULL',
    'is_verified': 'BOOLEAN DEFAULT 0',
    'page_is_verified': 'BOOLEAN DEFAULT 0',
    'posts_count': 'INTEGER NULL',
    'page_name': 'VARCHAR(255) NULL',
    'profile_id': 'VARCHAR(255) NULL',
}

# Add missing columns
for col_name, col_type in missing_columns.items():
    if col_name not in columns:
        try:
            print(f"Adding missing column: {col_name}")
            c.execute(f"ALTER TABLE facebook_data_facebookpost ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError as e:
            print(f"Error adding column {col_name}: {str(e)}")

# Commit the changes
conn.commit()

# Verify the columns now
c.execute("PRAGMA table_info(facebook_data_facebookpost)")
new_columns = {col[1]: col for col in c.fetchall()}
print(f"Now have {len(new_columns)} columns in the table")

# Close the connection
conn.close()

print("Database fix completed") 