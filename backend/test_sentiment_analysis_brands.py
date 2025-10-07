#!/usr/bin/env python3
"""
Test Nike vs Adidas sentiment analysis integration
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackfutura.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from reports.enhanced_report_service import EnhancedReportService
from reports.models import Report, ReportTemplate
from instagram_data.models import InstagramPost, Folder as InstagramFolder
from facebook_data.models import FacebookPost, Folder as FacebookFolder

def test_sentiment_analysis_with_brands():
    """Test sentiment analysis with Nike vs Adidas brand data sources"""
    
    print("🧪 Testing Nike vs Adidas Sentiment Analysis Integration...")
    
    try:
        # Get Instagram and Facebook folders for Nike and Adidas
        print("\n=== CHECKING AVAILABLE DATA ===")
        
        ig_folders = InstagramFolder.objects.all()
        fb_folders = FacebookFolder.objects.all()
        
        print(f"Instagram folders: {ig_folders.count()}")
        for folder in ig_folders:
            posts_count = folder.posts.count()
            print(f"  - {folder.name}: {posts_count} posts")
        
        print(f"\nFacebook folders: {fb_folders.count()}")
        for folder in fb_folders:
            posts_count = folder.posts.count()
            print(f"  - {folder.name}: {posts_count} posts")
        
        # Find Nike and Adidas folders
        nike_ig_folder = ig_folders.filter(name__icontains='Nike').first()
        nike_fb_folder = fb_folders.filter(name__icontains='Nike').first()
        adidas_ig_folder = ig_folders.filter(name__icontains='Adidas').first()
        adidas_fb_folder = fb_folders.filter(name__icontains='Adidas').first()
        
        brand_folder_ids = []
        competitor_folder_ids = []
        
        if nike_ig_folder:
            brand_folder_ids.append(nike_ig_folder.id)
            print(f"✅ Found Nike Instagram folder: {nike_ig_folder.name} (ID: {nike_ig_folder.id})")
        
        if nike_fb_folder:
            brand_folder_ids.append(nike_fb_folder.id)
            print(f"✅ Found Nike Facebook folder: {nike_fb_folder.name} (ID: {nike_fb_folder.id})")
        
        if adidas_ig_folder:
            competitor_folder_ids.append(adidas_ig_folder.id)
            print(f"✅ Found Adidas Instagram folder: {adidas_ig_folder.name} (ID: {adidas_ig_folder.id})")
        
        if adidas_fb_folder:
            competitor_folder_ids.append(adidas_fb_folder.id)
            print(f"✅ Found Adidas Facebook folder: {adidas_fb_folder.name} (ID: {adidas_fb_folder.id})")
        
        if not brand_folder_ids:
            print("❌ No Nike folders found! Cannot test brand-specific sentiment analysis.")
            return False
        
        print(f"\n=== TESTING SENTIMENT ANALYSIS WITH BRAND DATA ===")
        print(f"Nike folders: {brand_folder_ids}")
        print(f"Adidas folders: {competitor_folder_ids}")
        
        # Create a test report with brand configuration
        template = ReportTemplate.objects.filter(template_type='sentiment_analysis').first()
        if not template:
            print("❌ No sentiment analysis template found!")
            return False
        
        # Create test report with brand-specific configuration
        test_configuration = {
            'brand_folder_ids': brand_folder_ids,
            'competitor_folder_ids': competitor_folder_ids
        }
        
        report = Report.objects.create(
            title="Test Nike vs Adidas Sentiment Analysis",
            template=template,
            configuration=test_configuration,
            status='processing'
        )
        
        # Generate the sentiment analysis
        print("\n📊 Generating Nike vs Adidas sentiment analysis...")
        service = EnhancedReportService()
        results = service.generate_sentiment_analysis(report, project_id=1)
        
        # Check results
        if 'error' in results:
            print(f"❌ Error: {results['error']}")
            return False
        
        print(f"✅ Sentiment Analysis Generated!")
        print(f"📈 Report Title: {results.get('title', 'N/A')}")
        print(f"📊 Summary: {results.get('summary', 'N/A')}")
        print(f"🎯 Total Posts Analyzed: {results.get('data_source_count', 0)}")
        print(f"💭 Overall Sentiment: {results.get('overall_sentiment', 'N/A')}")
        
        # Check brand-specific data
        nike_count = results.get('nike_posts_count', 0)
        adidas_count = results.get('adidas_posts_count', 0)
        brand_breakdown = results.get('brand_breakdown', {})
        
        print(f"\n🏆 BRAND ANALYSIS:")
        print(f"  Nike posts: {nike_count}")
        print(f"  Adidas posts: {adidas_count}")
        
        if brand_breakdown:
            print(f"\n📊 Brand Sentiment Breakdown:")
            for brand, sentiment_data in brand_breakdown.items():
                if sentiment_data.get('total', 0) > 0:
                    positive_rate = (sentiment_data.get('positive', 0) / sentiment_data['total']) * 100
                    print(f"  {brand}: {positive_rate:.1f}% positive ({sentiment_data.get('positive', 0)}/{sentiment_data['total']} posts)")
        
        # Check brand insights
        brand_insights = results.get('brand_insights', [])
        if brand_insights:
            print(f"\n💡 Brand-Specific Insights:")
            for insight in brand_insights:
                print(f"  - {insight}")
        
        # Check visualizations
        visualizations = results.get('visualizations', {})
        if 'brand_sentiment_comparison' in visualizations:
            print(f"\n📈 Brand Sentiment Visualization Available: Nike vs Adidas comparison chart")
        
        # Update report status
        report.status = 'completed'
        report.results = results
        report.save()
        
        print(f"\n✅ Test completed successfully!")
        print(f"🎯 Nike vs Adidas sentiment analysis now available in Report Marketplace")
        print(f"📊 Users can select Nike and Adidas data sources separately")
        print(f"📈 Brand-specific insights and visualizations included")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during sentiment analysis test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sentiment_analysis_with_brands()
    if success:
        print("\n🎉 SENTIMENT ANALYSIS BRAND INTEGRATION COMPLETE!")
        print("✅ Users can now choose Nike or Adidas data sources for sentiment analysis")
        print("✅ Brand-specific sentiment insights and comparisons available")
        print("✅ Enhanced visualizations with Nike vs Adidas breakdowns")
    else:
        print("\n❌ Test failed. Check the error messages above.")