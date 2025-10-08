from brightdata_integration.models import BrightDataConfig

# Update Instagram configuration with API token
instagram_config = BrightDataConfig.objects.filter(platform='instagram').first()
if instagram_config:
    instagram_config.api_token = '8af6995e-3baa-4b69-9df7-8d7671e621eb'
    instagram_config.save()
    print(f'✅ Updated Instagram config (ID: {instagram_config.id}) with API token')
else:
    # Create Instagram configuration if it doesn't exist
    instagram_config = BrightDataConfig.objects.create(
        platform='instagram',
        name='Instagram Posts Scraper',
        dataset_id='gd_lk5ns7kz21pck8jpis',
        api_token='8af6995e-3baa-4b69-9df7-8d7671e621eb',
        is_active=True
    )
    print(f'✅ Created Instagram config (ID: {instagram_config.id})')

# Verify all configurations
configs = BrightDataConfig.objects.all()
for config in configs:
    has_token = bool(config.api_token)
    print(f'{config.platform}: ID={config.id}, Dataset={config.dataset_id}, Has_Token={has_token}')

print(f'Total configurations: {configs.count()}')
print('✅ Setup complete!')