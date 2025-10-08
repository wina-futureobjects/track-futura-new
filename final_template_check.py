#!/usr/bin/env python3
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackfutura.settings')
django.setup()

from reports.models import ReportTemplate

# Check template count
count = ReportTemplate.objects.count()
print(f"Total templates in production: {count}")

if count > 0:
    print("\nTemplate details:")
    for template in ReportTemplate.objects.all():
        print(f"- {template.name} ({template.template_type})")
        print(f"  ID: {template.id}")
        print(f"  Description: {template.description[:100]}...")
else:
    print("ERROR: No templates found!")
    print("Need to run: python manage.py populate_report_templates")