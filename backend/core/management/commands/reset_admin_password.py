from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Reset superadmin password for quick access'

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username='superadmin')
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS('✅ Password reset successful!'))
            self.stdout.write('Username: superadmin')
            self.stdout.write('Password: admin123')
            self.stdout.write('Login at: https://trackfutura.futureobjects.io/admin/')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Superadmin user not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))