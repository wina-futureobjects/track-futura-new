from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserRole, UserProfile, Organization, OrganizationMembership, Project
import random
from datetime import datetime, timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Creates comprehensive demo data including users, organizations, and projects for deployment demos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing demo data before creating new data',
        )
        parser.add_argument(
            '--users-count',
            type=int,
            default=15,
            help='Number of regular users to create (default: 15)',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('Resetting demo data...'))
            self.reset_demo_data()

        users_count = options['users_count']
        
        # Create admin users
        self.create_admin_users()
        
        # Create demo organizations
        organizations = self.create_demo_organizations()
        
        # Create regular users
        users = self.create_regular_users(users_count)
        
        # Assign users to organizations
        self.assign_users_to_organizations(users, organizations)
        
        # Create demo projects
        self.create_demo_projects(organizations)
        
        self.stdout.write(self.style.SUCCESS('Successfully created comprehensive demo data!'))
        self.print_summary(organizations, users)

    def reset_demo_data(self):
        """Delete existing demo data"""
        # Delete demo projects
        Project.objects.filter(name__contains='Demo').delete()
        
        # Delete demo organizations
        Organization.objects.filter(name__contains='Demo').delete()
        Organization.objects.filter(name__contains='TechCorp').delete()
        Organization.objects.filter(name__contains='Creative').delete()
        Organization.objects.filter(name__contains='Marketing').delete()
        
        # Delete demo users (except superuser)
        demo_usernames = [
            'superadmin', 'tenantadmin', 'alice.johnson', 'bob.smith', 
            'carol.davis', 'david.wilson', 'emma.brown', 'frank.miller',
            'grace.taylor', 'henry.clark', 'ivy.adams', 'jack.moore',
            'kate.white', 'liam.garcia', 'maya.lee', 'noah.hall',
            'olivia.young', 'peter.king', 'quinn.scott'
        ]
        User.objects.filter(username__in=demo_usernames).exclude(is_superuser=True).delete()
        
        self.stdout.write(self.style.SUCCESS('Demo data reset completed'))

    def create_admin_users(self):
        """Create admin users"""
        # Super Admin
        superadmin, created = User.objects.get_or_create(
            username='superadmin',
            defaults={
                'email': 'superadmin@trackfutura.com',
                'first_name': 'Super',
                'last_name': 'Admin',
                'is_active': True
            }
        )
        if created:
            superadmin.set_password('admin123!')
            superadmin.save()
            self.stdout.write(self.style.SUCCESS(f'Created Super Admin: {superadmin.username}'))
        
        UserProfile.objects.get_or_create(user=superadmin)
        UserRole.objects.update_or_create(
            user=superadmin,
            defaults={'role': 'super_admin'}
        )

        # Tenant Admin
        tenantadmin, created = User.objects.get_or_create(
            username='tenantadmin',
            defaults={
                'email': 'admin@trackfutura.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_active': True
            }
        )
        if created:
            tenantadmin.set_password('admin123!')
            tenantadmin.save()
            self.stdout.write(self.style.SUCCESS(f'Created Tenant Admin: {tenantadmin.username}'))
        
        UserProfile.objects.get_or_create(user=tenantadmin)
        UserRole.objects.update_or_create(
            user=tenantadmin,
            defaults={'role': 'tenant_admin'}
        )

    def create_demo_organizations(self):
        """Create demo organizations"""
        tenantadmin = User.objects.get(username='tenantadmin')
        
        organizations_data = [
            {
                'name': 'Demo TechCorp Solutions',
                'description': 'A technology company specializing in software development and digital transformation.',
                'owner': tenantadmin
            },
            {
                'name': 'Creative Marketing Agency',
                'description': 'Full-service marketing agency focused on brand development and digital campaigns.',
                'owner': tenantadmin
            },
            {
                'name': 'Global Analytics Inc',
                'description': 'Data analytics and business intelligence company serving enterprise clients.',
                'owner': tenantadmin
            }
        ]
        
        organizations = []
        for org_data in organizations_data:
            org, created = Organization.objects.get_or_create(
                name=org_data['name'],
                defaults=org_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created organization: {org.name}'))
            organizations.append(org)
            
            # Add owner as admin
            OrganizationMembership.objects.get_or_create(
                organization=org,
                user=org_data['owner'],
                defaults={'role': 'admin'}
            )
        
        return organizations

    def create_regular_users(self, count):
        """Create regular demo users with realistic names and emails"""
        users_data = [
            {'username': 'alice.johnson', 'first_name': 'Alice', 'last_name': 'Johnson', 'email': 'alice.johnson@example.com'},
            {'username': 'bob.smith', 'first_name': 'Bob', 'last_name': 'Smith', 'email': 'bob.smith@example.com'},
            {'username': 'carol.davis', 'first_name': 'Carol', 'last_name': 'Davis', 'email': 'carol.davis@example.com'},
            {'username': 'david.wilson', 'first_name': 'David', 'last_name': 'Wilson', 'email': 'david.wilson@example.com'},
            {'username': 'emma.brown', 'first_name': 'Emma', 'last_name': 'Brown', 'email': 'emma.brown@example.com'},
            {'username': 'frank.miller', 'first_name': 'Frank', 'last_name': 'Miller', 'email': 'frank.miller@example.com'},
            {'username': 'grace.taylor', 'first_name': 'Grace', 'last_name': 'Taylor', 'email': 'grace.taylor@example.com'},
            {'username': 'henry.clark', 'first_name': 'Henry', 'last_name': 'Clark', 'email': 'henry.clark@example.com'},
            {'username': 'ivy.adams', 'first_name': 'Ivy', 'last_name': 'Adams', 'email': 'ivy.adams@example.com'},
            {'username': 'jack.moore', 'first_name': 'Jack', 'last_name': 'Moore', 'email': 'jack.moore@example.com'},
            {'username': 'kate.white', 'first_name': 'Kate', 'last_name': 'White', 'email': 'kate.white@example.com'},
            {'username': 'liam.garcia', 'first_name': 'Liam', 'last_name': 'Garcia', 'email': 'liam.garcia@example.com'},
            {'username': 'maya.lee', 'first_name': 'Maya', 'last_name': 'Lee', 'email': 'maya.lee@example.com'},
            {'username': 'noah.hall', 'first_name': 'Noah', 'last_name': 'Hall', 'email': 'noah.hall@example.com'},
            {'username': 'olivia.young', 'first_name': 'Olivia', 'last_name': 'Young', 'email': 'olivia.young@example.com'},
            {'username': 'peter.king', 'first_name': 'Peter', 'last_name': 'King', 'email': 'peter.king@example.com'},
            {'username': 'quinn.scott', 'first_name': 'Quinn', 'last_name': 'Scott', 'email': 'quinn.scott@example.com'},
        ]
        
        users = []
        for i, user_data in enumerate(users_data[:count]):
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_active': True
                }
            )
            if created:
                user.set_password('demo123!')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created user: {user.username}'))
            
            # Create profile and role
            UserProfile.objects.get_or_create(user=user)
            UserRole.objects.update_or_create(
                user=user,
                defaults={'role': 'user'}
            )
            users.append(user)
        
        return users

    def assign_users_to_organizations(self, users, organizations):
        """Assign users to organizations with different roles"""
        roles = ['admin', 'member', 'viewer']
        
        for org in organizations:
            # Assign 5-8 users to each organization
            org_users = random.sample(users, random.randint(5, min(8, len(users))))
            
            for i, user in enumerate(org_users):
                # First user as admin, others random roles weighted towards member
                if i == 0:
                    role = 'admin'
                else:
                    role = random.choices(roles, weights=[1, 5, 2])[0]
                
                membership, created = OrganizationMembership.objects.get_or_create(
                    organization=org,
                    user=user,
                    defaults={'role': role}
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Added {user.username} as {role} to {org.name}')
                    )

    def create_demo_projects(self, organizations):
        """Create demo projects for each organization"""
        project_templates = [
            {
                'name': 'Social Media Campaign Q1',
                'description': 'Comprehensive social media marketing campaign targeting young professionals.',
                'is_public': True
            },
            {
                'name': 'Brand Analytics Dashboard',
                'description': 'Real-time dashboard for tracking brand mentions and sentiment analysis.',
                'is_public': False
            },
            {
                'name': 'Influencer Outreach Program',
                'description': 'Strategic influencer partnership program for product launches.',
                'is_public': True
            },
            {
                'name': 'Customer Engagement Study',
                'description': 'Detailed analysis of customer engagement patterns across platforms.',
                'is_public': False
            },
            {
                'name': 'Content Performance Metrics',
                'description': 'Tracking and optimization of content performance across all channels.',
                'is_public': True
            }
        ]
        
        for org in organizations:
            # Create 2-4 projects per organization
            num_projects = random.randint(2, 4)
            selected_projects = random.sample(project_templates, num_projects)
            
            # Get organization admin as project owner
            admin_membership = OrganizationMembership.objects.filter(
                organization=org, 
                role='admin'
            ).first()
            
            owner = admin_membership.user if admin_membership else org.owner
            
            for project_data in selected_projects:
                project_name = f"{project_data['name']} - {org.name.split()[0]}"
                
                project, created = Project.objects.get_or_create(
                    name=project_name,
                    defaults={
                        'description': project_data['description'],
                        'organization': org,
                        'owner': owner,
                        'is_public': project_data['is_public']
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Created project: {project.name}')
                    )
                    
                    # Add some authorized users to private projects
                    if not project.is_public:
                        org_members = OrganizationMembership.objects.filter(
                            organization=org
                        ).exclude(user=owner)[:2]
                        
                        for membership in org_members:
                            project.authorized_users.add(membership.user)

    def print_summary(self, organizations, users):
        """Print a summary of created demo data"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('DEMO DATA SUMMARY'))
        self.stdout.write('='*50)
        
        self.stdout.write(f'\nCreated {len(organizations)} Organizations:')
        for org in organizations:
            member_count = OrganizationMembership.objects.filter(organization=org).count()
            project_count = Project.objects.filter(organization=org).count()
            self.stdout.write(f'  • {org.name} ({member_count} members, {project_count} projects)')
        
        self.stdout.write(f'\nCreated {len(users)} Regular Users:')
        for user in users[:5]:  # Show first 5
            role = UserRole.objects.get(user=user).get_role_display()
            self.stdout.write(f'  • {user.get_full_name()} ({user.username}) - {role}')
        if len(users) > 5:
            self.stdout.write(f'  ... and {len(users) - 5} more users')
        
        self.stdout.write('\nAdmin Accounts:')
        self.stdout.write('  • superadmin / admin123! (Super Admin)')
        self.stdout.write('  • tenantadmin / admin123! (Tenant Admin)')
        
        self.stdout.write('\nRegular User Password: demo123!')
        self.stdout.write('\n' + '='*50) 