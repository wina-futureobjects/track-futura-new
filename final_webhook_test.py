#!/usr/bin/env python3
"""
Final end-to-end webhook test using the exact JSON structure from the user
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
from brightdata_integration.models import ScraperRequest, BrightdataConfig

def test_real_brightdata_webhook():
    """Test webhook with the exact JSON structure from BrightData"""

    print("🎯 FINAL WEBHOOK TEST - Real BrightData JSON Structure")
    print("=" * 60)

    # Exact JSON from the user's BrightData response
    real_brightdata_data = [
        {
            "url": "https://www.instagram.com/p/DKkbTWvJC37",
            "user_posted": "skybarauburnal",
            "description": "FRIDAY NIGHT - 7PM\n\nFRONT • BACK • BEER GARDEN\n\nSPECIALS 7–9!\nTRIVIA 7–9!\n\n@plato_jones + @misdemeanor.music UPFRONT\n@bigcityplowboys + @benbruud BACK\n\nEXCLUSIVE NEW BEERS AT THE NEW BEER GARDEN!",
            "hashtags": None,
            "num_comments": 1,
            "date_posted": "2025-06-06T18:19:52.000Z",
            "likes": 445,
            "photos": [
                "https://scontent-lax3-2.cdninstagram.com/v/t51.2885-15/504142011_18488011528067695_2498581221017936002_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-lax3-2.cdninstagram.com&_nc_cat=107&_nc_oc=Q6cZ2QEro9EUKW-Ky9LZIzqGHncpGzWMIZeMLg8_rVA9RblWsMZMEhcUpRLGRcVtloDp140&_nc_ohc=9kEgLT5xWegQ7kNvwFZRf5g&_nc_gid=auvWsiWYB4X8MUHPDW--_Q&edm=ANTKIIoBAAAA&ccb=7-5&oh=00_AfMEtvjurOfQ4d41Ge1msQk5vnrsUNZZWX_eUPcZcvbp1Q&oe=684D6922&_nc_sid=d885a2"
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

    # Create a new test folder
    test_folder = Folder.objects.create(
        name=f"Real BrightData Test {int(time.time())}",
        description="Test with real BrightData JSON structure"
    )
    print(f"📁 Created test folder: {test_folder.name} (ID: {test_folder.id})")

    # Get or create config
    config, created = BrightdataConfig.objects.get_or_create(
        platform='instagram_posts',
        defaults={'name': 'Real Test Config', 'dataset_id': 'real_test', 'is_active': True}
    )

    # Create scraper request with the snapshot_id that will be in the webhook
    snapshot_id = f"real_test_{int(time.time())}"
    scraper_request = ScraperRequest.objects.create(
        config=config,
        platform='instagram_posts',
        content_type='post',
        target_url='https://www.instagram.com/skybarauburnal/',
        num_of_posts=1,
        folder_id=test_folder.id,
        request_payload={'test': 'real_brightdata'},
        status='processing',
        request_id=snapshot_id  # THIS IS CRUCIAL - webhook matches on this field
    )
    print(f"📋 Created scraper request: ID {scraper_request.id}")

    # Get initial post count
    initial_post_count = InstagramPost.objects.filter(folder=test_folder).count()
    print(f"📊 Initial posts in folder: {initial_post_count}")

    # Prepare the webhook payload exactly as BrightData sends it
    webhook_payload = {
        "status": "running",
        "response_id": f"real_test_response_{int(time.time())}",
        "snapshot_id": snapshot_id,
        "data": real_brightdata_data
    }

    print(f"\n🌐 Testing webhook with real BrightData JSON structure")
    print(f"📦 Snapshot ID: {snapshot_id}")
    print(f"📦 Payload contains {len(real_brightdata_data)} Instagram post(s)")

    # Send webhook request
    webhook_url = "http://localhost:8000/api/brightdata/webhook/"

    try:
        response = requests.post(
            webhook_url,
            json=webhook_payload,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'BrightData-Webhook-Real-Test'
            },
            timeout=30
        )

        print(f"📡 Webhook response status: {response.status_code}")
        print(f"📝 Webhook response: {response.text}")

        if response.status_code != 200:
            print(f"❌ Webhook failed: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling webhook: {str(e)}")
        return False

    # Wait for processing
    time.sleep(2)

    # Check results
    final_post_count = InstagramPost.objects.filter(folder=test_folder).count()
    new_posts = final_post_count - initial_post_count

    print(f"\n📈 RESULTS:")
    print(f"   Final posts in folder: {final_post_count}")
    print(f"   New posts created: {new_posts}")

    if new_posts > 0:
        # Get the created post
        latest_post = InstagramPost.objects.filter(folder=test_folder).last()
        original_post = real_brightdata_data[0]

        print(f"\n✅ POST SUCCESSFULLY CREATED:")
        print(f"   • URL: {latest_post.url}")
        print(f"   • User: {latest_post.user_posted}")
        print(f"   • Description: {latest_post.description[:50]}...")
        print(f"   • Likes: {latest_post.likes}")
        print(f"   • Comments: {latest_post.num_comments}")
        print(f"   • Shortcode: {latest_post.shortcode}")
        print(f"   • Content Type: {latest_post.content_type}")
        print(f"   • Followers: {latest_post.followers}")
        print(f"   • Is Verified: {latest_post.is_verified}")
        print(f"   • Folder: {latest_post.folder.name}")

        # Verify critical fields match exactly
        print(f"\n🔍 FIELD VERIFICATION:")
        verifications = [
            ("URL", latest_post.url, original_post["url"]),
            ("User", latest_post.user_posted, original_post["user_posted"]),
            ("Post ID", latest_post.post_id, original_post["post_id"]),
            ("Likes", latest_post.likes, original_post["likes"]),
            ("Comments", latest_post.num_comments, original_post["num_comments"]),
            ("Shortcode", latest_post.shortcode, original_post["shortcode"]),
            ("Content Type", latest_post.content_type, original_post["content_type"]),
            ("User ID", latest_post.user_posted_id, original_post["user_posted_id"]),
            ("Followers", latest_post.followers, original_post["followers"]),
            ("Is Verified", latest_post.is_verified, original_post["is_verified"]),
        ]

        all_correct = True
        for field_name, db_value, original_value in verifications:
            if str(db_value) == str(original_value):
                print(f"   ✅ {field_name}: {db_value}")
            else:
                print(f"   ❌ {field_name}: DB={db_value}, Original={original_value}")
                all_correct = False

        if all_correct:
            print(f"\n🎉 SUCCESS: All field mappings are perfect!")
            return True
        else:
            print(f"\n⚠️  Some fields don't match exactly")
            return False
    else:
        print(f"\n❌ FAILED: No posts were created")
        return False

def main():
    """Run the final webhook test"""
    print("🚀 Starting Final Webhook Test with Real BrightData JSON")
    print("=" * 60)

    try:
        success = test_real_brightdata_webhook()

        print(f"\n" + "=" * 60)
        if success:
            print("🎉 FINAL TEST: PASSED ✅")
            print("✨ Instagram data from BrightData webhook is processed perfectly!")
            print("🔥 System is production-ready for your exact JSON structure!")
        else:
            print("❌ FINAL TEST: FAILED")
            print("⚠️  There are issues with the webhook processing")
        print("=" * 60)

        return success

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
