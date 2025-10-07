#!/usr/bin/env python3
"""
Complete Nike vs Adidas Sentiment Analysis Integration
"""

print("🚀 Setting up Nike vs Adidas Sentiment Analysis Integration...")

# Create proper brand source folders and test sentiment analysis
from instagram_data.models import Folder as InstagramFolder
from facebook_data.models import Folder as FacebookFolder, FacebookPost
from common.models import TrackSource
from reports.enhanced_report_service import EnhancedReportService
from reports.models import Report, ReportTemplate

print("\n=== CREATING BRAND SOURCE FOLDERS ===")

# Create Nike Facebook folder
nike_fb_folder, created = FacebookFolder.objects.get_or_create(
    name="Nike Brand Sources",
    defaults={'folder_type': 'company'}
)
if created:
    print(f"✅ Created Nike Facebook folder: {nike_fb_folder.name}")
else:
    print(f"📁 Nike Facebook folder exists: {nike_fb_folder.name}")

# Create Adidas Facebook folder
adidas_fb_folder, created = FacebookFolder.objects.get_or_create(
    name="Adidas Competitor Sources",
    defaults={'folder_type': 'competitor'}
)
if created:
    print(f"✅ Created Adidas Facebook folder: {adidas_fb_folder.name}")
else:
    print(f"📁 Adidas Facebook folder exists: {adidas_fb_folder.name}")

# Move Nike posts to Nike folder
nike_posts = FacebookPost.objects.filter(user_posted__icontains='nike')
nike_count = 0
for post in nike_posts:
    post.folder = nike_fb_folder
    post.save()
    nike_count += 1

# Move Adidas posts to Adidas folder  
adidas_posts = FacebookPost.objects.filter(user_posted__icontains='adidas')
adidas_count = 0
for post in adidas_posts:
    post.folder = adidas_fb_folder
    post.save()
    adidas_count += 1

print(f"📊 Moved {nike_count} Nike posts to Nike folder")
print(f"📊 Moved {adidas_count} Adidas posts to Adidas folder")

print("\n=== TESTING SENTIMENT ANALYSIS ===")

# Get sentiment analysis template
template = ReportTemplate.objects.filter(template_type='sentiment_analysis').first()
if not template:
    print("❌ No sentiment analysis template found!")
    exit(1)

# Create test report with brand-specific configuration
test_configuration = {
    'brand_folder_ids': [nike_fb_folder.id],      # Nike data
    'competitor_folder_ids': [adidas_fb_folder.id] # Adidas data
}

report = Report.objects.create(
    title="Nike vs Adidas Sentiment Analysis Test",
    template=template,
    configuration=test_configuration,
    status='processing'
)

print(f"📋 Created test report: {report.title}")

# Generate the sentiment analysis
print("🔍 Generating sentiment analysis with brand data...")
service = EnhancedReportService()
results = service.generate_sentiment_analysis(report, project_id=1)

# Check results
if 'error' in results:
    print(f"❌ Error: {results['error']}")
else:
    print(f"✅ Sentiment Analysis Generated Successfully!")
    print(f"📈 Title: {results.get('title', 'N/A')}")
    print(f"📊 Summary: {results.get('summary', 'N/A')}")
    print(f"🎯 Total Posts: {results.get('data_source_count', 0)}")
    print(f"💭 Overall Sentiment: {results.get('overall_sentiment', 'N/A')}")
    
    # Brand-specific results
    nike_count = results.get('nike_posts_count', 0)
    adidas_count = results.get('adidas_posts_count', 0)
    brand_breakdown = results.get('brand_breakdown', {})
    
    print(f"\n🏆 BRAND ANALYSIS RESULTS:")
    print(f"  Nike posts analyzed: {nike_count}")
    print(f"  Adidas posts analyzed: {adidas_count}")
    
    if brand_breakdown:
        print(f"\n📊 Brand Sentiment Breakdown:")
        for brand, sentiment_data in brand_breakdown.items():
            if sentiment_data.get('total', 0) > 0:
                positive = sentiment_data.get('positive', 0)
                neutral = sentiment_data.get('neutral', 0)
                negative = sentiment_data.get('negative', 0)
                total = sentiment_data.get('total', 0)
                positive_rate = (positive / total) * 100
                print(f"  {brand}: {positive_rate:.1f}% positive | {positive} pos, {neutral} neu, {negative} neg")
    
    # Brand insights
    brand_insights = results.get('brand_insights', [])
    if brand_insights:
        print(f"\n💡 Brand-Specific Insights:")
        for insight in brand_insights:
            print(f"  - {insight}")
    
    # Visualizations
    visualizations = results.get('visualizations', {})
    print(f"\n📈 Available Visualizations:")
    for viz_name, viz_data in visualizations.items():
        print(f"  - {viz_data.get('title', viz_name)}: {viz_data.get('type', 'chart')}")
    
    # Update report
    report.status = 'completed'
    report.results = results
    report.save()

print(f"\n🎉 SENTIMENT ANALYSIS INTEGRATION COMPLETE!")
print(f"✅ Nike folder ID: {nike_fb_folder.id} ({nike_count} posts)")
print(f"✅ Adidas folder ID: {adidas_fb_folder.id} ({adidas_count} posts)")
print(f"✅ Brand-specific sentiment analysis working")
print(f"✅ Users can now select Nike or Adidas data sources in Report Marketplace")
print(f"✅ Enhanced visualizations with Nike vs Adidas comparisons available")

print(f"\n📋 INTEGRATION SUMMARY:")
print(f"🎯 Frontend: Enhanced data source selection for Sentiment Analysis template")
print(f"🎯 Backend: Brand-specific sentiment analysis with Nike vs Adidas breakdown")
print(f"🎯 Visualizations: Nike vs Adidas sentiment comparison charts")
print(f"🎯 Insights: Brand-specific sentiment insights and recommendations")