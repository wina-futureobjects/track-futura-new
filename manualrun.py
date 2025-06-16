import requests

url = "https://api.brightdata.com/datasets/v3/trigger"
headers = {
	"Authorization": "Bearer c20a28d5-5c6c-43c3-9567-a6d7c193e727",
	"Content-Type": "application/json",
}
params = {
	"dataset_id": "gd_lk5ns7kz21pck8jpis",
	"endpoint": "https://api.upsun-deployment-xiwfmii-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/webhook/",
	"format": "json",
	"uncompressed_webhook": "true",
	"include_errors": "true",
	"type": "discover_new",
	"discover_by": "url",
}
data = [
	{"url":"https://www.instagram.com/oneshift","num_of_posts":2,"start_date":"01-01-2025","end_date":"06-16-2025","post_type":"Post"},
]

response = requests.post(url, headers=headers, params=params, json=data)
print(response.json())
