from brightdata_integration.models import BrightDataConfig
configs = BrightDataConfig.objects.all()
print("BrightData Configurations:")
for config in configs:
    print(f"Config {config.id}:")
    print(f"  Platform: {config.platform}")
    print(f"  Dataset ID: {config.dataset_id}")
    print(f"  API Token: {config.api_token[:20]}...")
    print(f"  Active: {config.is_active}")
    print()