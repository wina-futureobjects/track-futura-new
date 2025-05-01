import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()

# Get current table schema
c.execute("PRAGMA table_info(facebook_data_facebookpost)")
columns = {col[1]: col for col in c.fetchall()}
print(f"Found {len(columns)} columns in the table")

# Print all existing columns
print("Existing columns:")
for col in columns.keys():
    print(f"  - {col}")

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
    'profile_image_link': 'VARCHAR(500) NULL',
    'platform_type': 'VARCHAR(50) NULL',
    'location': 'VARCHAR(255) NULL',
    'latest_comments': 'TEXT NULL',
    'discovery_input': 'VARCHAR(255) NULL',
    'tagged_users': 'TEXT NULL',
    'page_intro': 'TEXT NULL',
    'page_category': 'VARCHAR(255) NULL',
    'page_phone': 'VARCHAR(50) NULL',
    'page_logo': 'VARCHAR(500) NULL',
    'page_external_website': 'VARCHAR(500) NULL',
    'page_likes': 'INTEGER NULL',
    'page_followers': 'INTEGER NULL',
    'page_url': 'VARCHAR(500) NULL',
    'num_comments': 'INTEGER NULL',
    'thumbnail': 'VARCHAR(500) NULL',
    'video_view_count': 'INTEGER NULL',
    'about': 'TEXT NULL',
    'is_paid_partnership': 'BOOLEAN DEFAULT 0',
    'engagement_score': 'REAL DEFAULT 0.0',
    'external_link': 'VARCHAR(500) NULL',
    'length': 'REAL NULL',
    'audio': 'VARCHAR(100) NULL',
    'days_range': 'INTEGER NULL',
    'num_of_posts': 'INTEGER NULL',
    'posts_to_not_include': 'TEXT NULL',
    'from_date': 'DATE NULL',
    'start_date': 'DATE NULL',
    'end_date': 'DATE NULL',
    'following': 'INTEGER NULL',
    'timestamp': 'DATETIME NULL',
    'active_ads_urls': 'TEXT NULL',
    'delegate_page_id': 'VARCHAR(255) NULL',
    'warning': 'TEXT NULL',
    'warning_code': 'VARCHAR(100) NULL',
    'error': 'TEXT NULL',
    'error_code': 'VARCHAR(100) NULL',
    'include_profile_data': 'BOOLEAN NULL',
    'is_page': 'BOOLEAN NULL',
    'link_description_text': 'TEXT NULL',
    'page_creation_time': 'DATETIME NULL',
    'page_email': 'VARCHAR(255) NULL',
    'page_price_range': 'VARCHAR(50) NULL',
    'page_reviewers_amount': 'INTEGER NULL',
    'page_reviews_score': 'VARCHAR(20) NULL',
    'until_date': 'DATE NULL',
    'input': 'TEXT NULL',
    'photos': 'TEXT NULL',
    'videos': 'TEXT NULL'
}

# Add missing columns
added_columns = []
for col_name, col_type in missing_columns.items():
    if col_name not in columns:
        try:
            print(f"Adding missing column: {col_name}")
            c.execute(f"ALTER TABLE facebook_data_facebookpost ADD COLUMN {col_name} {col_type}")
            added_columns.append(col_name)
        except sqlite3.OperationalError as e:
            print(f"Error adding column {col_name}: {str(e)}")

# Commit the changes
conn.commit()

# Verify the columns now
c.execute("PRAGMA table_info(facebook_data_facebookpost)")
new_columns = {col[1]: col for col in c.fetchall()}
print(f"Now have {len(new_columns)} columns in the table")

if added_columns:
    print("Added columns:")
    for col in added_columns:
        print(f"  - {col}")
else:
    print("No new columns needed to be added")

# Close the connection
conn.close()

print("Database fix completed") 