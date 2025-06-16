import requests
import json
import os

# Live Upsun webhook URL
LIVE_WEBHOOK_URL = "https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/"

# Load the Instagram data from the JSON file
def load_instagram_data():
    json_file_path = "bd_20250616_040447_0.json"
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"JSON file not found: {json_file_path}")
        return None

def test_live_webhook():
    print("🚀 Testing Live Upsun Webhook...")
    print(f"Webhook URL: {LIVE_WEBHOOK_URL}")

    # Load Instagram data
    webhook_data = load_instagram_data()
    if not webhook_data:
        print("❌ Failed to load Instagram data")
        return

    print(f"📊 Loaded {len(webhook_data)} entries from JSON file")

    # Count valid vs warning entries
    valid_entries = [entry for entry in webhook_data if entry.get('warning_code') != 'dead_page' and 'no posts found' not in entry.get('warning', '')]
    warning_entries = [entry for entry in webhook_data if entry.get('warning_code') == 'dead_page' or 'no posts found' in entry.get('warning', '')]

    print(f"✅ Valid entries: {len(valid_entries)}")
    print(f"⚠️  Warning entries: {len(warning_entries)}")

    # Prepare webhook payload
    payload = {
        'data': webhook_data,
        'job_id': 'test_live_webhook_20250116',
        'status': 'completed'
    }

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'BrightData-Webhook/1.0'
    }

    try:
        print("\n📡 Sending webhook request to live server...")
        response = requests.post(
            LIVE_WEBHOOK_URL,
            json=payload,
            headers=headers,
            timeout=30
        )

        print(f"📈 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("✅ Webhook request successful!")
            try:
                response_data = response.json()
                print(f"📄 Response Data: {json.dumps(response_data, indent=2)}")
            except:
                print(f"📄 Response Text: {response.text}")
        else:
            print(f"❌ Webhook request failed!")
            print(f"📄 Response Text: {response.text}")

    except requests.exceptions.Timeout:
        print("⏰ Request timed out after 30 seconds")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - could not reach the server")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
    except Exception as e:
        print(f"💥 Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_live_webhook()
