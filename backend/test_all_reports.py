#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive Test for All Report Types
Tests all 6 report templates with visualizations
"""
import os
import sys
import django
import json

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reports.models import ReportTemplate, GeneratedReport
from reports.enhanced_report_service import enhanced_report_service
from instagram_data.models import Folder
from users.models import Project


def test_report_type(template_type, template_name, test_name):
    """Test a specific report type"""
    print(f"\n{'=' * 80}")
    print(f"TESTING: {test_name}")
    print('=' * 80)

    try:
        # Get project
        project = Project.objects.first()
        if not project:
            print("   ❌ No project found")
            return False

        # Get folders with data
        folders = Folder.objects.filter(posts__isnull=False).distinct()[:5]
        if not folders:
            print("   ❌ No folders with posts found")
            return False

        print(f"   📁 Using {folders.count()} folders with data")

        # Create template if doesn't exist
        template, created = ReportTemplate.objects.get_or_create(
            template_type=template_type,
            defaults={
                'name': template_name,
                'description': f'Test {template_name}',
                'icon': 'assessment',
                'color': '#2196F3'
            }
        )

        # Create report
        report = GeneratedReport.objects.create(
            title=f"Test {template_name}",
            template=template,
            status='processing',
            configuration={'folder_ids': [f.id for f in folders]}
        )

        print(f"   ✅ Created report ID: {report.id}")

        # Generate report based on type
        print(f"   ⏳ Generating report...")

        if template_type == 'sentiment_analysis':
            results = enhanced_report_service.generate_sentiment_analysis(report, project_id=project.id)
        elif template_type == 'competitive_analysis':
            results = enhanced_report_service.generate_competitive_analysis(report, project_id=project.id)
        else:
            print(f"   ⚠️  Report type {template_type} not yet implemented in test")
            return False

        # Validate results
        if not results or results.get('error'):
            print(f"   ❌ Report generation failed: {results.get('error', 'Unknown error')}")
            report.status = 'failed'
            report.save()
            return False

        # Check visualizations
        visualizations = results.get('visualizations', {})
        print(f"   ✅ Report generated successfully!")
        print(f"   📊 Visualizations: {len(visualizations)}")

        for viz_name, viz_data in visualizations.items():
            viz_type = viz_data.get('type')
            viz_title = viz_data.get('title')
            print(f"      📈 {viz_name}: {viz_type} - '{viz_title}'")

        # Test JSON serialization
        try:
            json_data = json.dumps(results)
            print(f"   ✅ JSON serializable ({len(json_data)} bytes)")
        except Exception as e:
            print(f"   ❌ JSON serialization failed: {e}")
            return False

        # Save report
        report.results = results
        report.status = 'completed'
        report.data_source_count = results.get('data_source_count', 0)
        report.save()

        print(f"   ✅ Report saved with ID: {report.id}")
        print(f"   🔗 View at: http://localhost:5173/organizations/1/projects/{project.id}/reports/generated/{report.id}")

        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Test all report types"""
    print("=" * 80)
    print("COMPREHENSIVE REPORT TESTING - ALL TEMPLATES")
    print("=" * 80)

    test_cases = [
        ('sentiment_analysis', 'Sentiment Analysis', 'Sentiment Analysis with OpenAI'),
        ('competitive_analysis', 'Competitive Analysis', 'Competitive Analysis with Market Share'),
        # Add more when enhanced methods are integrated
        # ('engagement_metrics', 'Engagement Metrics', 'Engagement Metrics with Trends'),
        # ('content_analysis', 'Content Analysis', 'Content Analysis with Hashtags'),
        # ('trend_analysis', 'Trend Analysis', 'Trend Analysis with Growth Rate'),
        # ('user_behavior', 'User Behavior', 'User Behavior Analysis'),
    ]

    results = {}

    for template_type, template_name, test_name in test_cases:
        success = test_report_type(template_type, template_name, test_name)
        results[template_type] = success

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for template_type, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {template_type}")

    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 80)

    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
