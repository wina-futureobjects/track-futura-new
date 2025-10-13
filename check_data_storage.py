import requests

url = 'https://trackfutura.futureobjects.io/api/brightdata/data-storage/run/158/'
response = requests.get(url)
print(f'Data Storage Status: {response.status_code}')
data = response.json()
posts = data.get('posts', [])
print(f'Total posts found: {len(posts)}')

if posts:
    post = posts[0]
    print(f'Sample post content: {post.get("post_content", "N/A")[:100]}...')
    print(f'Webhook delivered flag: {post.get("webhook_delivered", False)}')
    print(f'Folder ID: {post.get("folder_id", "N/A")}')
else:
    print('No posts found in data storage')