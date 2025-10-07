#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reports.models import GeneratedReport, ReportTemplate
from reports.enhanced_report_service import enhanced_report_service

# Get the sentiment analysis template
try:
    template = ReportTemplate.objects.get(template_type='sentiment_analysis')
    print(f"Found template: {template.name}")
    
    # Create a test report configuration similar to what the frontend sends
    test_config = {
        'brand_folder_ids': [5],  # Nike SourceFolder ID for project 6
        'competitor_folder_ids': [6]  # Adidas SourceFolder ID for project 6
    }
    
    # Create a test report
    test_report = GeneratedReport.objects.create(
        title="Test Sentiment Analysis",
        template=template,
        configuration=test_config,
        status='processing'
    )
    
    print(f"Created test report: {test_report.id}")
    print("Configuration:", test_config)
    
    # Generate the report content
    result = enhanced_report_service.generate_sentiment_analysis(test_report, project_id=6)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Success! Data source count: {result.get('data_source_count', 0)}")
        
        # Check the actual result fields
        nike_count = result.get('nike_posts_count', 0)
        adidas_count = result.get('adidas_posts_count', 0)
        total_comments = result.get('total_comments', 0)
        
        print(f"Total comments processed: {total_comments}")
        print("Nike posts:", nike_count)
        print("Adidas posts:", adidas_count)
        
        brand_breakdown = result.get('brand_breakdown', {})
        print("Brand breakdown:", brand_breakdown)
        
        overall_sentiment = result.get('overall_sentiment', 'N/A')
        print(f"Overall sentiment: {overall_sentiment}")
        
        insights = result.get('insights', [])
        print(f"Insights: {len(insights)} items")
        
        visualizations = result.get('visualizations', {})
        print(f"Visualizations: {list(visualizations.keys())}")
    
    # Clean up
    test_report.delete()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()