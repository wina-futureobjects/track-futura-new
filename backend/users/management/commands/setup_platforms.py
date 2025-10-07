from django.core.management.base import BaseCommand
from users.models import Platform, Service, PlatformService

class Command(BaseCommand):
    help = 'Setup platforms and services for workflow management'

    def handle(self, *args, **options):
        self.stdout.write('Setting up platforms and services...')
        
        # Create Instagram platform
        instagram, created = Platform.objects.get_or_create(
            name='instagram',
            defaults={
                'display_name': 'Instagram',
                'description': 'Instagram social media platform',
                'is_enabled': True
            }
        )
        self.stdout.write(f'Instagram platform: {"created" if created else "exists"} - ID {instagram.id}')
        
        # Create Facebook platform
        facebook, created = Platform.objects.get_or_create(
            name='facebook',
            defaults={
                'display_name': 'Facebook',
                'description': 'Facebook social media platform',
                'is_enabled': True
            }
        )
        self.stdout.write(f'Facebook platform: {"created" if created else "exists"} - ID {facebook.id}')
        
        # Create Posts service
        posts, created = Service.objects.get_or_create(
            name='posts',
            defaults={
                'display_name': 'Posts Scraping',
                'description': 'Scrape posts from social media',
                'is_enabled': True
            }
        )
        self.stdout.write(f'Posts service: {"created" if created else "exists"} - ID {posts.id}')
        
        # Create Instagram + Posts platform service
        ig_posts, created = PlatformService.objects.get_or_create(
            platform=instagram,
            service=posts,
            defaults={
                'description': 'Instagram posts scraping service',
                'is_enabled': True
            }
        )
        self.stdout.write(f'Instagram-Posts service: {"created" if created else "exists"} - ID {ig_posts.id}')
        
        # Create Facebook + Posts platform service
        fb_posts, created = PlatformService.objects.get_or_create(
            platform=facebook,
            service=posts,
            defaults={
                'description': 'Facebook posts scraping service',
                'is_enabled': True
            }
        )
        self.stdout.write(f'Facebook-Posts service: {"created" if created else "exists"} - ID {fb_posts.id}')
        
        self.stdout.write(self.style.SUCCESS('✅ Platform setup complete!'))
        self.stdout.write(f'Platform count: {Platform.objects.count()}')
        self.stdout.write(f'Service count: {Service.objects.count()}')
        self.stdout.write(f'PlatformService count: {PlatformService.objects.count()}')