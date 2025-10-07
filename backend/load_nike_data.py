import requests
import json

# The Nike Instagram data you provided
nike_data = [
    {
        "id": 1,
        "caption": "Introducing NikeSKIMS. Designed to sculpt. Engineered to perform. A new brand for those who refuse to compromise. Arrives September 26 at 7am PT at nike.com, skims.com, and select Nike and SKIMS retail locations.",
        "ownerFullName": "Nike",
        "ownerUsername": "nike",
        "url": "https://www.instagram.com/p/DO58Q6hDiW7/",
        "commentsCount": 1516,
        "firstComment": "CHRIST IS KING ✝️",
        "likesCount": 78755,
        "timestamp": "2025-09-22T13:00:04.000Z"
    },
    {
        "id": 2,
        "caption": "Momentum lives in the collective. @ucla and @uscedu athletes take center stage in NikeSKIMS. NikeSKIMS arrives September 26 at 7am PT at nike.com, skims.com, and select Nike and SKIMS retail locations.",
        "ownerFullName": "Nike",
        "ownerUsername": "nike",
        "url": "https://www.instagram.com/p/DO6KTM7Drl1/",
        "commentsCount": 375,
        "firstComment": "STRONG!!!",
        "likesCount": 44153,
        "timestamp": "2025-09-22T15:00:10.000Z"
    },
    {
        "id": 3,
        "caption": "A win worth waiting for, what broke you then, built you now. @zoeharrison123 kicks help her side to victory on home soil.",
        "ownerFullName": "Nike",
        "ownerUsername": "nike",
        "url": "https://www.instagram.com/p/DPHPbgLDwpd/",
        "commentsCount": 101,
        "firstComment": "🙌",
        "likesCount": 18453,
        "timestamp": "2025-09-27T16:55:07.000Z"
    },
    {
        "id": 4,
        "caption": "Big stakes. Biggest stage. One way to find out. #JustDoIt",
        "ownerFullName": "Nike",
        "ownerUsername": "nike",
        "url": "https://www.instagram.com/p/DPIbjeAjlR9/",
        "commentsCount": 227,
        "firstComment": "🔥🔥🔥",
        "likesCount": 123249,
        "timestamp": "2025-09-28T04:00:18.000Z"
    },
    {
        "id": 5,
        "caption": "Every round earned. Every punch answered. @rorymcilroy, @officialtommyfleetwood, @robertmacintyre and Team Europe take home the Ryder Cup at Bethpage Black.",
        "ownerFullName": "Nike",
        "ownerUsername": "nike",
        "url": "https://www.instagram.com/p/DPKVkHmEhlc/",
        "commentsCount": 89,
        "firstComment": "🔥🔥🔥",
        "likesCount": 24973,
        "timestamp": "2025-09-28T21:47:24.000Z"
    }
]

headers = {'Authorization': 'Token e242daf2ea05576f08fb8d808aba529b0c7ffbab'}

# Let's update batch job 8 with this Nike data format
print("Updating batch job 8 with Nike Instagram data...")

# First check current data
r = requests.get('http://127.0.0.1:8000/api/apify/batch-jobs/8/results/', headers=headers)
if r.status_code == 200:
    current_data = r.json()
    print(f"Current batch job 8 has {len(current_data.get('results', []))} results")
    
print("\nThis script shows the Nike data format that should be returned by the API.")
print("Sample Nike post:")
print(json.dumps(nike_data[0], indent=2))