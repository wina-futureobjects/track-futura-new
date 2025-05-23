# Demo Data Setup for Track Futura

This guide explains how to set up demo data for Track Futura, making it easy to showcase the platform during deployment and demos.

## Quick Start

### Option 1: Using the Direct Script (Recommended)
```bash
cd backend
python seed_demo_data.py
```

### Option 2: Using Django Management Command
```bash
cd backend
python manage.py seed_demo_data
```

## Available Options

### Reset Existing Data
To clear existing demo data and create fresh data:
```bash
python seed_demo_data.py --reset
```

### Customize Number of Users
To create a specific number of regular users (default is 15):
```bash
python seed_demo_data.py --users 10
```

### Combine Options
```bash
python seed_demo_data.py --reset --users 20
```

## What Gets Created

### Admin Users
- **superadmin** / admin123! - Super Administrator with full system access
- **tenantadmin** / admin123! - Tenant Administrator for managing organizations

### Organizations
1. **Demo TechCorp Solutions** - Technology company specializing in software development
2. **Creative Marketing Agency** - Full-service marketing agency
3. **Global Analytics Inc** - Data analytics and business intelligence company

### Regular Users (15 by default)
All regular users have the password: **demo123!**

Sample users include:
- alice.johnson@example.com
- bob.smith@example.com
- carol.davis@example.com
- david.wilson@example.com
- And 11+ more realistic users...

### Projects
Each organization gets 2-4 projects with realistic names like:
- Social Media Campaign Q1
- Brand Analytics Dashboard
- Influencer Outreach Program
- Customer Engagement Study
- Content Performance Metrics

### Organization Memberships
- Users are randomly assigned to organizations with different roles (admin, member, viewer)
- Each organization has 5-8 members
- Role distribution is weighted towards 'member' role for realistic scenarios

## Demo Scenarios

### Super Admin Demo
Login as `superadmin` to demonstrate:
- System-wide user management
- Organization oversight
- Global analytics and reporting

### Tenant Admin Demo
Login as `tenantadmin` to demonstrate:
- Organization management
- Project creation and management
- User role assignment within organizations

### Regular User Demo
Login as any regular user (e.g., `alice.johnson`) to demonstrate:
- Project access based on organization membership
- Role-based permissions
- Collaborative features

## File Structure

```
backend/
├── users/management/commands/
│   ├── create_demo_users.py      # Original simple demo command
│   └── seed_demo_data.py         # Comprehensive seeding command
├── seed_demo_data.py             # Direct script runner
└── DEMO_DATA_SETUP.md           # This file
```

## Troubleshooting

### Migration Issues
If you get migration errors, ensure you've run:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Database Issues
If the database is locked or corrupted:
```bash
python manage.py shell -c "from django.db import connection; connection.close()"
```

### Reset Everything
To completely reset and recreate demo data:
```bash
python seed_demo_data.py --reset
```

## For Production Deployment

### Environment Variables
Make sure to set appropriate environment variables:
- `DJANGO_SETTINGS_MODULE=config.settings`
- Database configurations
- Security keys

### Database Setup
1. Ensure database is created and accessible
2. Run migrations: `python manage.py migrate`
3. Create superuser if needed: `python manage.py createsuperuser`
4. Run demo data seeding: `python seed_demo_data.py`

### Security Considerations
- Change default passwords in production
- Use environment-specific email domains
- Implement proper user authentication flows
- Consider creating organization-specific demo data

## Customization

### Adding More Organizations
Edit the `organizations_data` list in `seed_demo_data.py`:

```python
organizations_data = [
    {
        'name': 'Your Custom Organization',
        'description': 'Description of your organization',
        'owner': tenantadmin
    },
    # ... existing organizations
]
```

### Adding More Project Templates
Edit the `project_templates` list in `seed_demo_data.py`:

```python
project_templates = [
    {
        'name': 'Your Custom Project',
        'description': 'Project description',
        'is_public': True
    },
    # ... existing projects
]
```

### Custom User Data
Modify the `users_data` list to include users relevant to your demo scenario.

## Best Practices

1. **Run seeding after migrations**: Always ensure your database schema is up to date
2. **Use --reset for clean demos**: Start fresh for each major demo
3. **Document demo flows**: Create scripts for different demo scenarios
4. **Test user permissions**: Verify that role-based access works as expected
5. **Prepare data stories**: Have realistic use cases for each organization and project

## Integration with CI/CD

Add seeding to your deployment pipeline:

```bash
# In your deployment script
python manage.py migrate
python seed_demo_data.py --reset
```

This ensures fresh demo data is available after each deployment. 