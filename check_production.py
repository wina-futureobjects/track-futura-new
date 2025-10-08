from django.contrib.auth.models import User
from brightdata_integration.models import BrightDataConfig

user, created = User.objects.get_or_create(username='winam', defaults={'email': 'wina@futureobjects.io'})
user.set_password('Sniped@10')
user.save()
print(f'User: {user.username}')

configs = BrightDataConfig.objects.all()
print(f'Configs: {configs.count()}')
for c in configs:
    print(f'- {c.username} | {c.zone} | {c.is_enabled}')