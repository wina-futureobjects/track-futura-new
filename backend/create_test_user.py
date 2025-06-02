#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

def main():
    # Delete existing test user if it exists
    User.objects.filter(username='testuser').delete()
    
    # Create new test user
    user = User.objects.create_user(
        username='testuser',
        email='test@trackfutura.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    print(f"Created test user: {user.username} (password: testpass123)")

if __name__ == '__main__':
    main() 