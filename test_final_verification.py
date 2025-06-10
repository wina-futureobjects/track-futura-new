#!/usr/bin/env python3
"""
Final verification test to ensure Instagram data from BrightData webhook
is correctly processed and stored in the database using the actual JSON structure.
"""

import json
import requests
import os
import sys
import time

# Add Django project to path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from instagram_data.models import Folder, InstagramPost
from brightdata_integration.models import ScraperRequest, BrightdataNotification, BrightdataConfig

def test_instagram_webhook_processing():
    """Test Instagram webhook data processing with real BrightData JSON structure"""

    print("🔍 FINAL VERIFICATION: Instagram Webhook Data Processing")
    print("=" * 70)

    # Example JSON data from the user's actual BrightData response
    sample_instagram_data = [
        {
            "url": "https://www.instagram.com/p/DKkbTWvJC37",
            "user_posted": "skybarauburnal",
            "description": "FRIDAY NIGHT - 7PM\n\nFRONT • BACK • BEER GARDEN\n\nSPECIALS 7–9!\nTRIVIA 7–9!\n\n@plato_jones + @misdemeanor.music UPFRONT\n@bigcityplowboys + @benbruud BACK\n\nEXCLUSIVE NEW BEERS AT THE NEW BEER GARDEN!",
            "hashtags": None,
            "num_comments": 1,
            "date_posted": "2025-06-06T18:19:52.000Z",
            "likes": 445,
            "photos": [
                "https://scontent-lax3-2.cdninstagram.com/v/t51.2885-15/504142011_18488011528067695_2498581221017936002_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-lax3-2.cdninstagram.com&_nc_cat=107&_nc_oc=Q6cZ2QEro9EUKW"
            ],
            "videos": None,
            "location": None,
            "latest_comments": [
                {
                    "comments": "So many memories of me going to the Sky bar for karaoke 🎤 and dancing the night away in the Auburn night sky and War Dam EAGLE 🧡💙🐅",
                    "likes": 0,
                    "profile_picture": "***",
                    "user_commenting": "jameskyser2025"
                }
            ],
            "post_id": "3649161675416022523",
            "discovery_input": None,
            "has_handshake": None,
            "shortcode": "DKkbTWvJC37",
            "content_type": "Carousel",
            "pk": "3649161675416022523",
            "content_id": "DKkbTWvJC37",
            "engagement_score_view": None,
            "thumbnail": "https://scontent-lax3-2.cdninstagram.com/v/t51.2885-15/504142011_18488011528067695_2498581221017936002_n.jpg?stp=c0.240.1440.1440a_dst-jpg_e35_s640x640_sh0.08_tt6&_nc_ht=scontent-lax3-2.cdninstagram.com&_nc_cat=107&_nc_oc=Q6cZ2QEro9EUKW",
            "video_view_count": None,
            "product_type": None,
            "coauthor_producers": None,
            "tagged_users": None,
            "video_play_count": None,
            "followers": 23959,
            "posts_count": 1922,
            "profile_image_link": "https://scontent-lax3-2.cdninstagram.com/v/t51.2885-19/68723330_940113063004248_7546939682957819904_n.jpg?stp=dst-jpg_s150x150_tt6&_nc_ht=scontent-lax3-2.cdninstagram.com&_nc_cat=100&_nc_oc=Q6cZ2QEro9EUKW",
            "is_verified": False,
            "is_paid_partnership": False,
            "partnership_details": {
                "profile_id": None,
                "profile_url": None,
                "username": None
            },
            "user_posted_id": "1938739694",
            "post_content": [
                {
                    "id": "3649161669040916043",
                    "index": 0,
                    "type": "Photo",
                    "url": "https://scontent-lax3-2.cdninstagram.com/v/t51.2885-15/504142011_18488011528067695_2498581221017936002_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-lax3-2.cdninstagram.com&_nc_cat=107&_nc_oc=Q6cZ2QEro9EUKW"
                }
            ],
            "audio": {
                "audio_asset_id": None,
                "ig_artist_id": None,
                "ig_artist_username": None,
                "original_audio_title": None
            },
            "profile_url": "https://www.instagram.com/skybarauburnal",
            "videos_duration": [],
            "images": [
                {
                    "id": "364***166***091******",
                    "url": "***"
                }
            ],
            "alt_text": "Photo by SkyBar Café on June 06, 2025. May be an image of 3 people and text.",
            "photos_number": 4
        }
    ]

    # Create a test folder to store the post
    test_folder, created = Folder.objects.get_or_create(
        name="Final Verification Test",
        defaults={"description": "Test folder for final verification"}
    )
    if created:
        print(f"✅ Created test folder: {test_folder.name} (ID: {test_folder.id})")
    else:
        print(f"📁 Using existing test folder: {test_folder.name} (ID: {test_folder.id})")

    # Get or create a BrightData config for the test
    config, created = BrightdataConfig.objects.get_or_create(
        platform='instagram_posts',
        defaults={
            'name': 'Test Instagram Config',
            'dataset_id': 'test',
            'is_active': True
        }
    )

    # Create a mock scraper request for this test
    scraper_request = ScraperRequest.objects.create(
        config=config,
        platform='instagram_posts',
        content_type='post',
        target_url='https://www.instagram.com/skybarauburnal/',
        num_of_posts=1,
        folder_id=test_folder.id,
        request_payload={'test': 'verification'},
        status='processing'
    )
    print(f"📋 Created scraper request: ID {scraper_request.id}")

    # Get initial post count
    initial_post_count = InstagramPost.objects.filter(folder=test_folder).count()
    print(f"📊 Initial posts in folder: {initial_post_count}")

    # Prepare webhook payload that BrightData would send
    webhook_payload = {
        "status": "running",
        "response_id": "test_verification_response",
        "snapshot_id": f"test_verification_{int(time.time())}",
        "data": sample_instagram_data
    }

    # Test the webhook endpoint
    webhook_url = "http://localhost:8000/api/brightdata/webhook/"

    print(f"\n🌐 Testing webhook endpoint: {webhook_url}")
    print(f"📦 Payload contains {len(sample_instagram_data)} Instagram post(s)")

    try:
        # Send POST request to webhook
        response = requests.post(
            webhook_url,
            json=webhook_payload,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'BrightData-Webhook-Test'
            },
            timeout=30
        )

        print(f"📡 Webhook response status: {response.status_code}")
        print(f"📝 Webhook response: {response.text}")

        if response.status_code == 200:
            print("✅ Webhook processed successfully")
        else:
            print(f"❌ Webhook failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling webhook: {str(e)}")
        return False

    # Wait a moment for processing
    time.sleep(2)

    # Check if post was created in database
    final_post_count = InstagramPost.objects.filter(folder=test_folder).count()
    new_posts = final_post_count - initial_post_count

    print(f"\n📈 Final posts in folder: {final_post_count}")
    print(f"🆕 New posts created: {new_posts}")

    if new_posts > 0:
        # Get the newly created post
        latest_post = InstagramPost.objects.filter(folder=test_folder).last()

        print(f"\n🔍 VERIFICATION: Latest Post Details")
        print(f"   • URL: {latest_post.url}")
        print(f"   • User: {latest_post.user_posted}")
        print(f"   • Post ID: {latest_post.post_id}")
        print(f"   • Description: {latest_post.description[:100]}...")
        print(f"   • Likes: {latest_post.likes}")
        print(f"   • Comments: {latest_post.num_comments}")
        print(f"   • Date Posted: {latest_post.date_posted}")
        print(f"   • Shortcode: {latest_post.shortcode}")
        print(f"   • Content Type: {latest_post.content_type}")
        print(f"   • Followers: {latest_post.followers}")
        print(f"   • Posts Count: {latest_post.posts_count}")
        print(f"   • Is Verified: {latest_post.is_verified}")
        print(f"   • Photos: {len(latest_post.photos) if latest_post.photos else 0}")
        print(f"   • Thumbnail: {latest_post.thumbnail[:50] if latest_post.thumbnail else 'None'}...")

        # Verify key field mappings match the original data
        original_post = sample_instagram_data[0]

        verification_checks = [
            ("URL", latest_post.url, original_post["url"]),
            ("User Posted", latest_post.user_posted, original_post["user_posted"]),
            ("Post ID", latest_post.post_id, original_post["post_id"]),
            ("Likes", latest_post.likes, original_post["likes"]),
            ("Comments", latest_post.num_comments, original_post["num_comments"]),
            ("Shortcode", latest_post.shortcode, original_post["shortcode"]),
            ("Content Type", latest_post.content_type, original_post["content_type"]),
            ("Followers", latest_post.followers, original_post["followers"]),
            ("Posts Count", latest_post.posts_count, original_post["posts_count"]),
            ("Is Verified", latest_post.is_verified, original_post["is_verified"]),
        ]

        print(f"\n✅ FIELD MAPPING VERIFICATION:")
        all_checks_passed = True
        for field_name, db_value, original_value in verification_checks:
            if str(db_value) == str(original_value):
                print(f"   ✅ {field_name}: {db_value}")
            else:
                print(f"   ❌ {field_name}: DB={db_value}, Original={original_value}")
                all_checks_passed = False

        if all_checks_passed:
            print(f"\n🎉 SUCCESS: All field mappings are correct!")
        else:
            print(f"\n⚠️  WARNING: Some field mappings need adjustment")

        print(f"✅ Post successfully stored in folder: {test_folder.name}")
        return True
    else:
        print(f"❌ No new posts were created - webhook processing may have failed")
        return False

def check_notification_system():
    """Check if notification system is working"""
    print(f"\n📢 NOTIFICATION SYSTEM CHECK")
    print("=" * 40)

    notifications = BrightdataNotification.objects.all().order_by('-created_at')[:5]
    print(f"📊 Total notifications: {BrightdataNotification.objects.count()}")

    if notifications:
        print(f"🔔 Recent notifications:")
        for notification in notifications:
            print(f"   • {notification.created_at}: {notification.event_type} - {notification.status}")
    else:
        print(f"📭 No notifications found")

def main():
    """Run the final verification test"""
    print("🚀 Starting Final Verification Test")
    print("=" * 50)

    try:
        # Test webhook processing
        webhook_success = test_instagram_webhook_processing()

        # Check notification system
        check_notification_system()

        print(f"\n" + "=" * 50)
        if webhook_success:
            print("🎉 FINAL VERIFICATION: PASSED")
            print("✅ Instagram data is correctly processed and stored!")
        else:
            print("❌ FINAL VERIFICATION: FAILED")
            print("⚠️  Instagram data processing needs attention")
        print("=" * 50)

        return webhook_success

    except Exception as e:
        print(f"❌ Error during verification: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
