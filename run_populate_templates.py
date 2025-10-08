#!/usr/bin/env python
"""
Run the populate_report_templates command in production
"""
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command

def populate_templates():
    print("🔧 POPULATING REPORT TEMPLATES")
    print("="*50)
    
    try:
        # Run the management command
        call_command('populate_report_templates')
        print("✅ Templates populated successfully!")
        
        # Verify templates were created
        from reports.models import ReportTemplate
        template_count = ReportTemplate.objects.count()
        print(f"📊 Total templates in database: {template_count}")
        
        if template_count > 0:
            print("✅ Report Marketplace should now show templates!")
        else:
            print("❌ No templates found after population")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = populate_templates()
    
    if success:
        print("\n🎉 SUCCESS! Report templates are now available!")
        print("🌐 Refresh the report marketplace page to see templates")
    else:
        print("\n💡 MANUAL STEPS:")
        print("   1. Check if populate_report_templates.py exists")
        print("   2. Run: python manage.py populate_report_templates")
        print("   3. Or create templates manually via Django admin")