#!/usr/bin/env python
"""
Test script to generate enhanced competitive analysis with improved AI insights
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reports.enhanced_report_service import EnhancedReportService
from reports.models import Report
from users.models import Project, Organization
from common.data_integration_service import DataIntegrationService
from facebook_data.models import FacebookPost
import json

def test_enhanced_competitive_analysis():
    """Test the enhanced competitive analysis with better AI insights"""
    print("🤖 TESTING ENHANCED COMPETITIVE ANALYSIS:")
    
    # Get or create test objects
    org, _ = Organization.objects.get_or_create(name="Test Org")
    project, _ = Project.objects.get_or_create(name="Nike vs Adidas Analysis", organization=org)
    
    # Create or get a competitive analysis report
    report, created = Report.objects.get_or_create(
        title="Enhanced Nike vs Adidas Competitive Analysis",
        template_type="competitive_analysis",
        project=project,
        defaults={
            'status': 'completed',
            'results': {}
        }
    )
    
    if created:
        print(f"✅ Created new report: {report.title}")
    else:
        print(f"📊 Using existing report: {report.title}")
    
    # Initialize enhanced report service
    enhanced_service = EnhancedReportService()
    
    try:
        # Generate competitive analysis with enhanced AI insights
        result = enhanced_service.generate_competitive_analysis(report, project_id=project.id)
        
        print(f"\n📈 ENHANCED ANALYSIS RESULTS:")
        print(f"   Title: {result.get('title')}")
        print(f"   Data Source Count: {result.get('data_source_count')}")
        print(f"   Processing Time: {result.get('processing_time')} seconds")
        
        # Show competitor metrics
        competitor_metrics = result.get('competitor_metrics', [])
        print(f"\n🏆 COMPETITOR METRICS:")
        for metric in competitor_metrics:
            print(f"   {metric.get('name')}: {metric.get('total_likes'):,} likes, {metric.get('total_comments'):,} comments, {metric.get('market_share'):.1f}% market share")
        
        # Show AI insights
        insights = result.get('insights', [])
        print(f"\n� AI INSIGHTS ({len(insights)} insights):")
        for i, insight in enumerate(insights, 1):
            if isinstance(insight, str) and insight.strip():
                print(f"   {i}. {insight}")
            elif isinstance(insight, dict):
                print(f"   {i}. [OBJECT] {insight}")
        
        # Show recommendations
        recommendations = result.get('recommendations', [])
        print(f"\n💡 RECOMMENDATIONS ({len(recommendations)} recommendations):")
        for i, rec in enumerate(recommendations, 1):
            if isinstance(rec, str) and rec.strip():
                print(f"   {i}. {rec}")
            elif isinstance(rec, dict):
                print(f"   {i}. [OBJECT] {rec}")
        
        # Show opportunities
        opportunities = result.get('opportunities', [])
        print(f"\n🚀 OPPORTUNITIES ({len(opportunities)} opportunities):")
        for i, opp in enumerate(opportunities, 1):
            if isinstance(opp, str) and opp.strip():
                print(f"   {i}. {opp}")
            elif isinstance(opp, dict):
                print(f"   {i}. [OBJECT] {opp}")
        
        # Update the report with new results
        report.results = result
        report.save()
        print(f"\n✅ Report updated with enhanced analysis (ID: {report.id})")
        
        return report.id
        
    except Exception as e:
        print(f"❌ Error generating enhanced competitive analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_data_integration():
    """Test data integration and competitive analysis"""
    print("🔍 TESTING DATA INTEGRATION:")
    
    # Initialize service
    data_service = DataIntegrationService()
    
    # Get company and competitor data
    company_posts = data_service.get_company_posts(limit=10)
    competitor_posts = data_service.get_competitor_posts(limit=10)
    
    print(f"📊 Company posts (Nike): {len(company_posts)}")
    print(f"🥊 Competitor posts (Adidas): {len(competitor_posts)}")
    
    # Show sample data
    if company_posts:
        sample_company = company_posts[0]
        print(f"Sample Company Post: User={sample_company.get('user')}, Likes={sample_company.get('likes')}")
    
    if competitor_posts:
        sample_competitor = competitor_posts[0]
        print(f"Sample Competitor Post: User={sample_competitor.get('user')}, Likes={sample_competitor.get('likes')}")

def test_direct_facebook_data():
    """Test direct Facebook data access"""
    print("\n📘 TESTING DIRECT FACEBOOK DATA:")
    
    # Get all Facebook posts
    posts = FacebookPost.objects.all()[:10]
    
    nike_posts = []
    adidas_posts = []
    
    for post in posts:
        user_posted = post.user_posted
        if isinstance(user_posted, dict):
            name = user_posted.get('name', '').lower()
        else:
            name = str(user_posted).lower()
        
        if 'nike' in name:
            nike_posts.append(post)
        elif 'adidas' in name:
            adidas_posts.append(post)
    
    print(f"Direct Nike posts found: {len(nike_posts)}")
    print(f"Direct Adidas posts found: {len(adidas_posts)}")
    
    # Calculate total metrics
    nike_total_likes = sum(post.likes or 0 for post in nike_posts)
    nike_total_comments = sum(post.num_comments or 0 for post in nike_posts)
    adidas_total_likes = sum(post.likes or 0 for post in adidas_posts)
    adidas_total_comments = sum(post.num_comments or 0 for post in adidas_posts)
    
    print(f"Nike: {nike_total_likes} likes, {nike_total_comments} comments")
    print(f"Adidas: {adidas_total_likes} likes, {adidas_total_comments} comments")

if __name__ == "__main__":
    test_direct_facebook_data()
    test_data_integration()
    report_id = test_enhanced_competitive_analysis()
    if report_id:
        print(f"\n🎯 Access the enhanced report at: http://localhost:5185/organizations/5/projects/6/reports/competitive-analysis/{report_id}")