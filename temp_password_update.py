import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackfutura.settings')
django.setup()

from django.contrib.auth.models import User

user = User.objects.get(username='superadmin')
user.set_password('admin123')
user.save()
print('Password updated successfully!')