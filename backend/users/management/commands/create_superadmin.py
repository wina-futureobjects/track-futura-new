from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserRole, UserProfile, Organization
from django.db import transaction


class Command(BaseCommand):
    help = 'Create superadmin user with username superadmin and password admin123'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                self.stdout.write(self.style.SUCCESS("Setting up superadmin user..."))

                # Get or create superadmin user
                admin_user, created = User.objects.get_or_create(
                    username='superadmin',
                    defaults={
                        'email': 'superadmin@trackfutura.com',
                        'is_staff': True,
                        'is_superuser': True,
                        'is_active': True,
                    }
                )

                # Set password regardless of whether user was created or already existed
                admin_user.set_password('admin123')
                admin_user.save()

                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created superadmin user: {admin_user.username}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Updated existing superadmin user: {admin_user.username}'))

                # Get or create super_admin role
                user_role, role_created = UserRole.objects.get_or_create(
                    user=admin_user,
                    defaults={
                        'role': 'super_admin'
                    }
                )

                if role_created:
                    self.stdout.write(self.style.SUCCESS(f'Created super_admin role for user: {user_role.role}'))
                else:
                    # Update existing role to super_admin
                    user_role.role = 'super_admin'
                    user_role.save()
                    self.stdout.write(self.style.SUCCESS(f'Updated existing role to super_admin: {user_role.role}'))

                # Get or create user profile
                profile, profile_created = UserProfile.objects.get_or_create(
                    user=admin_user,
                    defaults={
                        'global_role': user_role
                    }
                )

                if profile_created:
                    self.stdout.write(self.style.SUCCESS(f'Created new profile for superadmin'))
                else:
                    profile.global_role = user_role
                    profile.save()
                    self.stdout.write(self.style.SUCCESS(f'Updated existing superadmin profile'))

                # Make sure Future Objects organization exists
                future_objects_org, org_created = Organization.objects.get_or_create(
                    name='Future Objects',
                    defaults={
                        'description': 'Main organization for super administrators',
                        'created_by': admin_user
                    }
                )

                if org_created:
                    self.stdout.write(self.style.SUCCESS(f'Created Future Objects organization'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Future Objects organization already exists'))

                self.stdout.write(self.style.SUCCESS(f'Final superadmin user role: {user_role.role}'))
                self.stdout.write(self.style.SUCCESS(f'Superadmin user login: superadmin/admin123'))
                self.stdout.write(self.style.SUCCESS('✅ Superadmin setup completed successfully!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating superadmin: {str(e)}'))
            raise e