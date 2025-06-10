import requests
import json

def test_webhooks():
    base_url = 'http://localhost:8000'

    print('🧪 Testing Track-Futura Webhook System')
    print('=' * 50)

    # Test 1: Server health
    try:
        response = requests.get(f'{base_url}/api/health/', timeout=5)
        if response.status_code == 200:
            print('✅ Server Health: OK')
        else:
            print(f'❌ Server Health: Status {response.status_code}')
    except Exception as e:
        print(f'❌ Server Health: {e}')

    # Test 2: Webhook health
    try:
        response = requests.get(f'{base_url}/api/brightdata/webhook/health/', timeout=5)
        if response.status_code == 200:
            print('✅ Webhook Health: OK')
            data = response.json()
            status = data.get('health', {}).get('status', 'unknown')
            print(f'   Status: {status}')
        else:
            print(f'❌ Webhook Health: Status {response.status_code}')
    except Exception as e:
        print(f'❌ Webhook Health: {e}')

    # Test 3: Webhook authentication
    try:
        webhook_token = 'your-default-webhook-secret-token-change-this'
        payload = json.dumps([{
            'url': 'https://test.com',
            'platform': 'facebook'
        }])
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {webhook_token}'
        }

        response = requests.post(f'{base_url}/api/brightdata/webhook/',
                               data=payload, headers=headers, timeout=5)

        if response.status_code in [200, 400, 500]:
            print('✅ Webhook Authentication: Token accepted')
        elif response.status_code == 401:
            print('❌ Webhook Authentication: Token rejected')
        else:
            print(f'⚠️ Webhook Authentication: Status {response.status_code}')

    except Exception as e:
        print(f'❌ Webhook Authentication: {e}')

    print('=' * 50)
    print('✅ Webhook testing completed!')

if __name__ == '__main__':
    test_webhooks()
