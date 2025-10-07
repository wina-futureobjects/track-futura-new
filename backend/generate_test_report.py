#!/usr/bin/env python
"""Generate a test Sentiment Analysis report with fixed pie chart data"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reports.models import ReportTemplate, GeneratedReport
from reports.enhanced_report_service import EnhancedReportService

print("="*60)
print("GENERATING TEST SENTIMENT ANALYSIS REPORT")
print("="*60)

# Get template
template = ReportTemplate.objects.get(template_type='sentiment_analysis')
print(f"\nTemplate: {template.name}")

# Create report
report = GeneratedReport.objects.create(
    template=template,
    title='PIE CHART FIX TEST REPORT',
    status='processing',
    configuration={'folder_ids': [12]}
)
print(f"Report ID: {report.id}")
print("Status: Processing...")

# Generate using enhanced service
service = EnhancedReportService()
results = service.generate_sentiment_analysis(report, project_id=1)

# Save results
report.results = results
report.status = 'completed'
report.save()

print(f"\nStatus: Completed!")
print(f"Report ID: {report.id}")

# Check the chart data format
viz_data = results.get('visualizations', {}).get('sentiment_distribution', {}).get('data', {})

print("\n" + "="*60)
print("PIE CHART DATA STRUCTURE:")
print("="*60)
print(json.dumps(viz_data, indent=2))

# Validate
has_datasets = 'datasets' in viz_data
has_labels = 'labels' in viz_data
has_old_values = 'values' in viz_data

print("\n" + "="*60)
print("VALIDATION:")
print("="*60)
print(f"Has 'labels': {has_labels}")
print(f"Has 'datasets' (Chart.js): {has_datasets}")
print(f"Has 'values' (old format): {has_old_values}")

if has_datasets and not has_old_values:
    print("\nSUCCESS! Chart data is in correct Chart.js format!")
    if viz_data.get('datasets'):
        ds = viz_data['datasets'][0]
        print(f"  - data: {ds.get('data')}")
        print(f"  - backgroundColor: {ds.get('backgroundColor')}")
else:
    print("\nFAILED! Chart data is still in old format!")

print("\n" + "="*60)
print(f"View report at: http://localhost:5173/reports/sentiment-analysis/{report.id}")
print("="*60)
