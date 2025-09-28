"""
Management command to test deployment configuration
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
import os


class Command(BaseCommand):
    help = 'Test deployment configuration'

    def handle(self, *args, **options):
        self.stdout.write("Testing deployment configuration...")

        # Test database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.stdout.write(
                    self.style.SUCCESS("✓ Database connection successful")
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Database connection failed: {e}")
            )
            return

        # Test static files configuration
        if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Static root configured: {settings.STATIC_ROOT}")
            )
        else:
            self.stdout.write(
                self.style.WARNING("⚠ Static root not configured")
            )

        # Test environment variables
        critical_vars = [
            'DJANGO_SETTINGS_MODULE',
        ]

        for var in critical_vars:
            if os.environ.get(var):
                self.stdout.write(
                    self.style.SUCCESS(f"✓ {var} is set")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"⚠ {var} not set")
                )

        # Test optional variables
        optional_vars = [
            'OPENAI_API_KEY',
            'BRIGHTDATA_WEBHOOK_BASE_URL',
        ]

        for var in optional_vars:
            if os.environ.get(var):
                self.stdout.write(
                    self.style.SUCCESS(f"✓ {var} is configured")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"⚠ {var} not configured (optional)")
                )

        # Test security settings
        if not settings.DEBUG:
            security_checks = [
                ('SECURE_SSL_REDIRECT', getattr(settings, 'SECURE_SSL_REDIRECT', False)),
                ('SECURE_BROWSER_XSS_FILTER', getattr(settings, 'SECURE_BROWSER_XSS_FILTER', False)),
                ('SECURE_CONTENT_TYPE_NOSNIFF', getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', False)),
            ]

            for check_name, check_value in security_checks:
                if check_value:
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ {check_name} enabled")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"⚠ {check_name} disabled")
                    )

        self.stdout.write(
            self.style.SUCCESS("Deployment configuration test completed!")
        )