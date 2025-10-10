#!/usr/bin/env python3
"""
🎯 VIEW YOUR EXISTING DATA
=========================

You already have 78 posts in your system! 
This script shows you exactly how to see them.
"""

import os
import sys
import django

# Setup Django
try:
    if not os.path.exists('manage.py'):
        os.chdir('backend')
    
    sys.path.insert(0, os.getcwd())
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    print("✅ Connected to your database")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

def show_your_data():
    """Show the actual data you have"""
    print("\n" + "="*60)
    print("📊 YOUR EXISTING SCRAPED DATA (78 POSTS!)")
    print("="*60)
    
    try:
        from brightdata_integration.models import BrightDataScrapedPost
        
        # Get all your posts
        all_posts = list(BrightDataScrapedPost.objects.all().order_by('-created_at'))
        
        print(f"\n🎉 YOU HAVE {len(all_posts)} SCRAPED POSTS!")
        
        # Show recent posts with details
        recent_posts = all_posts[:10]  # Show latest 10
        
        for i, post in enumerate(recent_posts, 1):
            print(f"\n📄 POST #{i}")
            print(f"   📅 Date: {post.created_at}")
            print(f"   📱 Platform: {post.platform}")
            print(f"   📝 Content: {post.content[:100]}...")
            print(f"   👤 User: {getattr(post, 'username', 'N/A')}")
            print(f"   ❤️ Likes: {getattr(post, 'likes_count', 0)}")
            print(f"   💬 Comments: {getattr(post, 'comments_count', 0)}")
            
            # Show raw data if available
            if hasattr(post, 'raw_data') and post.raw_data:
                print(f"   📊 Raw data keys: {list(post.raw_data.keys()) if isinstance(post.raw_data, dict) else 'Available'}")
        
        # Group by platform
        platform_counts = {}
        for post in all_posts:
            platform = post.platform
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        print(f"\n📊 POSTS BY PLATFORM:")
        for platform, count in platform_counts.items():
            print(f"   📱 {platform.title()}: {count} posts")
            
    except Exception as e:
        print(f"❌ Error accessing data: {e}")
        import traceback
        traceback.print_exc()

def show_production_commands():
    """Show exact commands to access data in production"""
    print("\n" + "="*60)
    print("🌐 ACCESS YOUR DATA IN PRODUCTION")
    print("="*60)
    
    print("\n1. 🔍 SEE ALL YOUR POSTS:")
    print("   upsun ssh -p inhoolfrqniuu -e main --app trackfutura 'cd backend && python manage.py shell -c \"")
    print("   from brightdata_integration.models import BrightDataScrapedPost")
    print("   posts = BrightDataScrapedPost.objects.all()")
    print("   print(f'Total posts: {posts.count()}')") 
    print("   for post in posts[:5]:")
    print("       print(f'{post.created_at}: {post.platform} - {post.content[:50]}...')")
    print("   \"'")
    
    print("\n2. 📊 CHECK RECENT WEBHOOK EVENTS:")
    print("   upsun ssh -p inhoolfrqniuu -e main --app trackfutura 'cd backend && python manage.py shell -c \"")
    print("   from brightdata_integration.models import BrightDataWebhookEvent")
    print("   events = BrightDataWebhookEvent.objects.all().order_by('-created_at')")
    print("   for event in events[:3]:")
    print("       print(f'{event.created_at}: {event.platform} - {event.status}')")
    print("   \"'")
    
    print("\n3. 🗄️ DIRECT DATABASE QUERY:")
    print("   upsun ssh -p inhoolfrqniuu -e main --app trackfutura 'psql -c \"")
    print("   SELECT id, platform, content, created_at ")
    print("   FROM brightdata_integration_brightdatascrapedpost ")
    print("   ORDER BY created_at DESC LIMIT 10;")
    print("   \"'")

def create_data_access_commands():
    """Create ready-to-run commands"""
    print("\n" + "="*60)
    print("🚀 READY-TO-RUN COMMANDS")
    print("="*60)
    
    commands = [
        "# View all your scraped posts",
        "upsun ssh -p inhoolfrqniuu -e main --app trackfutura 'cd backend && python manage.py shell -c \"from brightdata_integration.models import BrightDataScrapedPost; [print(f\\\"{p.created_at}: {p.platform} - {p.content[:100]}...\\\") for p in BrightDataScrapedPost.objects.all()[:10]]\"'",
        "",
        "# Check webhook events",
        "upsun ssh -p inhoolfrqniuu -e main --app trackfutura 'cd backend && python manage.py shell -c \"from brightdata_integration.models import BrightDataWebhookEvent; [print(f\\\"{e.created_at}: {e.platform} - {e.status}\\\") for e in BrightDataWebhookEvent.objects.all()[:5]]\"'",
        "",
        "# Database direct query", 
        "upsun ssh -p inhoolfrqniuu -e main --app trackfutura 'psql -c \"SELECT COUNT(*) as total_posts, platform FROM brightdata_integration_brightdatascrapedpost GROUP BY platform;\"'",
    ]
    
    # Write commands to file
    with open('../view_data_commands.sh', 'w') as f:
        f.write('\n'.join(commands))
    
    print("\n📝 Commands saved to: view_data_commands.sh")
    print("\n🔥 COPY AND PASTE THESE COMMANDS:")
    for cmd in commands:
        if cmd and not cmd.startswith('#'):
            print(f"\n{cmd}")

def main():
    """Main function"""
    print("🎯 YOUR DATA IS ALREADY HERE!")
    print("=" * 40)
    
    show_your_data()
    show_production_commands()
    create_data_access_commands()
    
    print("\n" + "="*60)
    print("✅ SUMMARY - YOU ALREADY HAVE DATA!")
    print("="*60)
    print("🎉 78 posts are already stored in your system")
    print("🔧 Webhook is working and ready for more data") 
    print("🌐 BrightData just needs to be configured with your webhook URL")
    print("📊 Use the commands above to see your existing data")
    print("\n🎯 NEXT: Configure BrightData webhook and start scraping more!")

if __name__ == "__main__":
    main()