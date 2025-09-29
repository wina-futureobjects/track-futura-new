from django.core.management.base import BaseCommand
from apify_integration.models import ApifyConfig
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sets up default Apify configurations for various social media platforms.'

    def add_arguments(self, parser):
        parser.add_argument('--api-token', type=str, required=True, help='Your Apify API token.')

    def handle(self, *args, **options):
        api_token = options['api_token']
        
        # Define platform configurations
        platforms = [
            ('facebook_posts', 'Facebook Posts', 'apify/facebook-scraper'),
            ('facebook_reels', 'Facebook Reels', 'apify/facebook-scraper'),
            ('facebook_comments', 'Facebook Comments', 'apify/facebook-scraper'),
            ('instagram_posts', 'Instagram Posts', 'apify/instagram-scraper'),
            ('instagram_reels', 'Instagram Reels', 'apify/instagram-scraper'),
            ('instagram_comments', 'Instagram Comments', 'apify/instagram-scraper'),
            ('linkedin_posts', 'LinkedIn Posts', 'apify/linkedin-scraper'),
            ('tiktok_posts', 'TikTok Posts', 'apify/tiktok-scraper'),
        ]
        
        created_count = 0
        updated_count = 0
        
        for platform, name, actor_id in platforms:
            config, created = ApifyConfig.objects.get_or_create(
                platform=platform,
                defaults={
                    'name': name,
                    'api_token': api_token,
                    'actor_id': actor_id,
                    'is_active': True,
                    'description': f'Default configuration for {name}'
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'Created config: {name}')
            else:
                # Update existing config with new API token
                config.api_token = api_token
                config.save()
                updated_count += 1
                self.stdout.write(f'Updated config: {name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Setup complete! Created: {created_count}, Updated: {updated_count}')
        )
