from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Project

class Command(BaseCommand):
    help = 'Setup default project for Web Unlocker integration'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get or create superuser
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.create_superuser(
                username='admin',
                email='admin@trackfutura.com',
                password='admin123'
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created superuser: {user.username}')
            )
        else:
            self.stdout.write(f'✅ Found superuser: {user.username}')
        
        # Get or create project
        project = Project.objects.first()
        if not project:
            project = Project.objects.create(
                name="TrackFutura Main Project",
                description="Main project for BrightData Web Unlocker integration",
                owner=user
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created project: {project.name} (ID: {project.id})')
            )
        else:
            self.stdout.write(f'✅ Found project: {project.name} (ID: {project.id})')
        
        self.stdout.write(
            self.style.SUCCESS(f'🎯 Project ID {project.id} ready for Web Unlocker endpoint')
        )
        
        return project.id