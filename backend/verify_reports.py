import os
import sys
import django

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reports.models import GeneratedReport

# Get the new reports
r52 = GeneratedReport.objects.get(id=52)
r54 = GeneratedReport.objects.get(id=54)

print("=" * 60)
print("VERIFICATION: Reports Have Different Visualizations")
print("=" * 60)

print("\n✅ Report 52 (Sentiment Analysis):")
print(f"   Template Type: {r52.template.template_type}")
print(f"   Visualization Keys: {list(r52.results['visualizations'].keys())}")
for key, viz in r52.results['visualizations'].items():
    print(f"     - {key}: {viz['type']} chart - {viz['title']}")

print("\n✅ Report 54 (Engagement Metrics):")
print(f"   Template Type: {r54.template.template_type}")
print(f"   Visualization Keys: {list(r54.results['visualizations'].keys())}")
for key, viz in r54.results['visualizations'].items():
    print(f"     - {key}: {viz['type']} chart - {viz['title']}")

print("\n" + "=" * 60)
viz_keys_52 = set(r52.results['visualizations'].keys())
viz_keys_54 = set(r54.results['visualizations'].keys())

if viz_keys_52 != viz_keys_54:
    print("✅ CONFIRMED: Reports have DIFFERENT visualizations!")
    print(f"   Sentiment has: {viz_keys_52}")
    print(f"   Engagement has: {viz_keys_54}")
else:
    print("❌ ERROR: Reports have SAME visualizations!")

print("=" * 60)
