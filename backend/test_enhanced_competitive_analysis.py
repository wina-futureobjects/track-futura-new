#!/usr/bin/env python3

import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_enhanced_competitive_analysis():
    """Test the enhanced competitive analysis with Nike vs Adidas data integration"""
    print("=== TESTING ENHANCED COMPETITIVE ANALYSIS ===\n")
    
    from reports.enhanced_report_service import enhanced_report_service
    from reports.models import GeneratedReport, ReportTemplate
    
    # Create a mock report for testing
    template, created = ReportTemplate.objects.get_or_create(
        template_type='competitive_analysis',
        defaults={
            'name': 'Competitive Analysis',
            'description': 'Nike vs Adidas competitive analysis'
        }
    )
    
    report = GeneratedReport.objects.create(
        title="Nike vs Adidas Competitive Analysis Test",
        template=template,
        status='processing',
        configuration={}
    )
    
    print(f"1. Created test report: {report.id}")
    
    # Generate competitive analysis with project ID 6 (demo project)
    print("2. Generating competitive analysis...")
    results = enhanced_report_service.generate_competitive_analysis(report, project_id=6)
    
    if results.get('error'):
        print(f"❌ Error: {results['error']}")
        return False
    
    print(f"✅ Competitive Analysis Generated!")
    print(f"📊 Title: {results['title']}")
    print(f"📈 Summary: {results['summary']}")
    print(f"🔢 Data Source Count: {results['data_source_count']}")
    
    if 'brands' in results:
        print(f"\n🏆 Brand Analysis:")
        for brand in results['brands'][:3]:
            print(f"  - {brand['name']}: {brand['post_count']} posts, {brand['avg_engagement']:,} avg engagement")
            print(f"    Market Share: {brand['market_share']}%, Type: {brand['brand_type']}")
    
    if 'nike_vs_adidas' in results.get('competitive_analysis', {}):
        nike_vs_adidas = results['competitive_analysis']['nike_vs_adidas']
        print(f"\n⚡ Nike vs Adidas Performance:")
        
        if 'nike_performance' in nike_vs_adidas:
            nike = nike_vs_adidas['nike_performance']
            print(f"  Nike: {nike.get('avg_likes', 0):,} avg likes, {nike.get('market_share', 0)}% market share")
        
        if 'adidas_performance' in nike_vs_adidas:
            adidas = nike_vs_adidas['adidas_performance']
            print(f"  Adidas: {adidas.get('avg_likes', 0):,} avg likes, {adidas.get('market_share', 0)}% market share")
    
    # Test insights
    insights = results.get('insights', [])
    print(f"\n💡 Top Insights ({len(insights)}):")
    for i, insight in enumerate(insights[:3], 1):
        print(f"  {i}. {insight}")
    
    # Test visualizations
    visualizations = results.get('visualizations', {})
    print(f"\n📊 Visualizations Available:")
    for viz_name, viz_data in visualizations.items():
        print(f"  - {viz_name}: {viz_data.get('type', 'unknown')} chart - {viz_data.get('title', 'No title')}")
    
    # Update report with results
    report.results = results
    report.status = 'completed'
    report.save()
    
    print(f"\n✅ Report {report.id} saved with enhanced competitive analysis!")
    print("✅ Nike vs Adidas comparison ready for frontend!")
    
    return True

if __name__ == "__main__":
    test_enhanced_competitive_analysis()