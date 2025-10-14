"""
Production Project Creation Management Command
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import Project
from django.db import transaction

class Command(BaseCommand):
    help = 'Create project ID 1 for Web Unlocker in production'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Creating Production Project for Web Unlocker")
        
        with transaction.atomic():
            # Get or create superuser
            superuser = User.objects.filter(is_superuser=True).first()
            if not superuser:
                superuser = User.objects.create_superuser(
                    username='admin',
                    email='admin@trackfutura.com',
                    password='TrackFutura2024!'
                )
                self.stdout.write(f"✅ Created superuser: {superuser.username}")
            else:
                self.stdout.write(f"✅ Using superuser: {superuser.username}")
            
            # Check if project 1 exists
            project_1 = Project.objects.filter(id=1).first()
            
            if not project_1:
                # Create project with ID 1
                from django.db import connection
                
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO users_project (id, name, description, owner_id, is_public, created_at, updated_at)
                        VALUES (1, 'Web Unlocker Project', 'Default project for Web Unlocker', %s, FALSE, NOW(), NOW())
                        ON CONFLICT (id) DO NOTHING
                    """, [superuser.id])
                
                project_1 = Project.objects.get(id=1)
                self.stdout.write(f"✅ Created project ID 1: {project_1.name}")
            else:
                self.stdout.write(f"✅ Project ID 1 exists: {project_1.name}")
        
        # Verify
        projects = Project.objects.all()
        self.stdout.write(f"📊 Total projects: {projects.count()}")
        self.stdout.write("🎉 Production project setup complete!")