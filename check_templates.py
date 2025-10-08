from reports.models import ReportTemplate

# Check how many templates exist
count = ReportTemplate.objects.count()
print(f"Total templates in production: {count}")

if count > 0:
    print("\nTemplate details:")
    for template in ReportTemplate.objects.all():
        print(f"- {template.name} ({template.template_type})")
else:
    print("No templates found - need to run populate_report_templates")