#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive Test for All 6 Report Templates
Tests each template with real database data
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


# Import enhanced methods
from reports import enhanced_methods


class MockViewSet:
    """Mock viewset to hold enhanced methods"""
    pass


# Attach methods to mock viewset
mock_viewset = MockViewSet()
mock_viewset._process_engagement_metrics_ENHANCED = enhanced_methods._process_engagement_metrics_ENHANCED.__get__(mock_viewset)
mock_viewset._process_content_analysis_ENHANCED = enhanced_methods._process_content_analysis_ENHANCED.__get__(mock_viewset)
mock_viewset._process_trend_analysis_ENHANCED = enhanced_methods._process_trend_analysis_ENHANCED.__get__(mock_viewset)
mock_viewset._process_user_behavior_ENHANCED = enhanced_methods._process_user_behavior_ENHANCED.__get__(mock_viewset)


def test_report(template_type, template_name, generator_func):
    """Test a specific report type"""
    print(f"\n{'=' * 80}")
    print(f"TESTING: {template_name}")
    print('=' * 80)

    try:
        # Get project
        project = Project.objects.first()
        if not project:
            print("   ❌ No project found")
            return False, None

        # Get folders with data
        folders = Folder.objects.filter(posts__isnull=False).distinct()[:5]
        if not folders:
            print("   ❌ No folders with posts found")
            return False, None

        print(f"   📁 Using {folders.count()} folders with data")

        # Create template
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
        print(f"   ⏳ Generating report...")

        # Generate report
        results = generator_func(report, project_id=project.id)

        # Validate results
        if not results or results.get('error'):
            print(f"   ❌ Report generation failed: {results.get('error', 'Unknown error')}")
            report.status = 'failed'
            report.save()
            return False, report.id

        # Check key metrics
        print(f"   ✅ Report generated successfully!")

        # Display report type
        print(f"   📊 Report Type: {results.get('report_type', 'N/A')}")

        # Display data source count
        data_count = results.get('data_source_count', 0)
        print(f"   📈 Data Points: {data_count}")

        # Check visualizations
        visualizations = results.get('visualizations', {})
        print(f"   📊 Visualizations: {len(visualizations)}")

        for viz_name, viz_data in visualizations.items():
            viz_type = viz_data.get('type')
            viz_title = viz_data.get('title')
            print(f"      📈 {viz_name}: {viz_type} - '{viz_title}'")

        # Display insights
        insights = results.get('insights', [])
        if insights:
            print(f"   💡 Insights: {len(insights)}")
            for insight in insights[:2]:
                print(f"      • {insight}")

        # Test JSON serialization
        try:
            json_data = json.dumps(results)
            print(f"   ✅ JSON serializable ({len(json_data)} bytes)")
        except Exception as e:
            print(f"   ❌ JSON serialization failed: {e}")
            return False, report.id

        # Save report
        report.results = results
        report.status = 'completed'
        report.data_source_count = data_count
        report.save()

        print(f"   ✅ Report saved with ID: {report.id}")
        print(f"   🔗 View at: http://localhost:5173/organizations/1/projects/{project.id}/reports/generated/{report.id}")

        return True, report.id

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def main():
    """Test all 6 report types"""
    print("=" * 80)
    print("COMPREHENSIVE TEST - ALL 6 REPORT TEMPLATES")
    print("=" * 80)

    test_cases = [
        ('sentiment_analysis', 'Sentiment Analysis',
         lambda r, **kw: enhanced_report_service.generate_sentiment_analysis(r, **kw)),

        ('competitive_analysis', 'Competitive Analysis',
         lambda r, **kw: enhanced_report_service.generate_competitive_analysis(r, **kw)),

        ('engagement_metrics', 'Engagement Metrics',
         lambda r, **kw: mock_viewset._process_engagement_metrics_ENHANCED(r, **kw)),

        ('content_analysis', 'Content Analysis',
         lambda r, **kw: mock_viewset._process_content_analysis_ENHANCED(r, **kw)),

        ('trend_analysis', 'Trend Analysis',
         lambda r, **kw: mock_viewset._process_trend_analysis_ENHANCED(r, **kw)),

        ('user_behavior', 'User Behavior',
         lambda r, **kw: mock_viewset._process_user_behavior_ENHANCED(r, **kw)),
    ]

    results = {}
    report_ids = {}

    for template_type, template_name, generator in test_cases:
        success, report_id = test_report(template_type, template_name, generator)
        results[template_type] = success
        report_ids[template_type] = report_id

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for template_type, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        report_id = report_ids.get(template_type, 'N/A')
        print(f"{status}: {template_type.ljust(25)} (Report ID: {report_id})")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! All 6 report templates are working correctly.")
        print("\n📊 Report URLs:")
        project = Project.objects.first()
        for template_type, report_id in report_ids.items():
            if report_id:
                print(f"   • {template_type}: http://localhost:5173/organizations/1/projects/{project.id}/reports/generated/{report_id}")

    print("=" * 80)

    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
