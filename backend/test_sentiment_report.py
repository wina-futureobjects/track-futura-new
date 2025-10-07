#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
End-to-End Test for Sentiment Analysis Report
Tests the complete flow from data to visualization-ready report
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
from users.models import Project

def test_sentiment_analysis_report():
    print("=" * 80)
    print("END-TO-END SENTIMENT ANALYSIS REPORT TEST")
    print("=" * 80)

    # Step 1: Get project
    print("\n1. Getting test project...")
    project = Project.objects.first()
    if not project:
        print("   ❌ No project found. Please create a project first.")
        return False
    print(f"   ✅ Using project ID: {project.id}")

    # Step 2: Get or create Sentiment Analysis template
    print("\n2. Getting Sentiment Analysis template...")
    template, created = ReportTemplate.objects.get_or_create(
        template_type='sentiment_analysis',
        defaults={
            'name': 'Sentiment Analysis',
            'description': 'Analyze the sentiment of comments and feedback to understand public opinion about your brand',
            'icon': 'psychology',
            'color': '#9C27B0',
            'estimated_time': '2-5 minutes',
            'required_data_types': ['comments', 'posts'],
            'features': [
                'Positive/Negative/Neutral classification',
                'Confidence scores for each sentiment',
                'Trending keywords analysis',
                'Platform-specific sentiment breakdown'
            ]
        }
    )
    print(f"   ✅ Template: {template.name} (ID: {template.id})")

    # Step 3: Create a test report
    print("\n3. Creating test report...")
    report = GeneratedReport.objects.create(
        title="Test Sentiment Analysis - Nike Brand",
        template=template,
        status='processing',
        configuration={
            'batch_job_ids': [17, 16, 15, 14, 8],  # Use batch jobs with actual data
            'folder_ids': []
        }
    )
    print(f"   ✅ Created report ID: {report.id}")

    # Step 4: Generate the report
    print("\n4. Generating sentiment analysis...")
    try:
        results = enhanced_report_service.generate_sentiment_analysis(report, project_id=project.id)

        print(f"   ✅ Report generated successfully!")
        print(f"   📊 Report Type: {results.get('report_type')}")
        print(f"   📝 Summary: {results.get('summary')}")
        print(f"   💭 Overall Sentiment: {results.get('overall_sentiment', 'N/A').upper()}")

        # Display sentiment breakdown
        sentiment_breakdown = results.get('sentiment_breakdown', {})
        print(f"\n   Sentiment Breakdown:")
        print(f"      ✅ Positive: {sentiment_breakdown.get('positive', 0)}")
        print(f"      ➖ Neutral: {sentiment_breakdown.get('neutral', 0)}")
        print(f"      ❌ Negative: {sentiment_breakdown.get('negative', 0)}")

        # Display sentiment percentages
        sentiment_percentages = results.get('sentiment_percentages', {})
        if sentiment_percentages:
            print(f"\n   Sentiment Percentages:")
            print(f"      ✅ Positive: {sentiment_percentages.get('positive', 0):.1f}%")
            print(f"      ➖ Neutral: {sentiment_percentages.get('neutral', 0):.1f}%")
            print(f"      ❌ Negative: {sentiment_percentages.get('negative', 0):.1f}%")

        # Display insights
        insights = results.get('insights', [])
        if insights:
            print(f"\n   💡 Insights:")
            for insight in insights[:5]:
                print(f"      • {insight}")

        # Check visualizations
        visualizations = results.get('visualizations', {})
        print(f"\n5. Checking visualizations...")
        if visualizations:
            print(f"   ✅ Found {len(visualizations)} visualizations:")
            for viz_name, viz_data in visualizations.items():
                viz_type = viz_data.get('type', 'unknown')
                viz_title = viz_data.get('title', 'Untitled')
                print(f"      📊 {viz_name}: {viz_type} chart - '{viz_title}'")

                # Validate chart data
                chart_data = viz_data.get('data', {})
                if viz_type == 'pie':
                    labels = chart_data.get('labels', [])
                    values = chart_data.get('values', [])
                    print(f"         Labels: {labels}")
                    print(f"         Values: {values}")
                elif viz_type == 'bar':
                    labels = chart_data.get('labels', [])
                    datasets = chart_data.get('datasets', [])
                    print(f"         Labels: {labels}")
                    print(f"         Datasets: {len(datasets)}")
        else:
            print(f"   ⚠️ No visualizations found")

        # Save report
        print(f"\n6. Saving report...")
        report.results = results
        report.status = 'completed'
        report.data_source_count = results.get('data_source_count', 0)
        report.save()
        print(f"   ✅ Report saved successfully")
        print(f"   📈 Data source count: {report.data_source_count}")
        print(f"   ⏱️  Processing time: {results.get('processing_time', 0)} seconds")

        # Test JSON serialization
        print(f"\n7. Testing JSON serialization...")
        try:
            json_data = json.dumps(results, indent=2)
            print(f"   ✅ Report is JSON serializable ({len(json_data)} characters)")
        except Exception as e:
            print(f"   ❌ JSON serialization failed: {e}")
            return False

        # Display report URL
        print(f"\n8. Report Details:")
        print(f"   📄 Report ID: {report.id}")
        print(f"   📊 Template: {report.template.name}")
        print(f"   ✅ Status: {report.status}")
        print(f"   🔗 View at: http://localhost:5173/organizations/1/projects/{project.id}/reports/generated/{report.id}")

        return True

    except Exception as e:
        print(f"   ❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()

        # Update report status
        report.status = 'failed'
        report.error_message = str(e)
        report.save()
        return False

if __name__ == "__main__":
    success = test_sentiment_analysis_report()

    print("\n" + "=" * 80)
    if success:
        print("✅ SENTIMENT ANALYSIS REPORT TEST PASSED")
        print("   The report is ready to be displayed with visualizations!")
    else:
        print("❌ SENTIMENT ANALYSIS REPORT TEST FAILED")
        print("   Check the errors above for details")
    print("=" * 80)
