#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reports.openai_service import report_openai_service

def test_nike_brand_analysis():
    """Test the updated Nike brand analysis"""
    print("🧪 Testing Nike Brand Performance Report...")
    
    try:
        # Generate sentiment analysis report (Nike brand analysis)
        print("📊 Generating Nike Brand Intelligence Report...")
        sentiment_report = report_openai_service.generate_sentiment_analysis_report(project_id=1)
        
        print(f"\n✅ Nike Brand Analysis Complete!")
        print(f"📈 Data Source: {sentiment_report.get('data_source', 'Unknown')}")
        print(f"🎯 Posts Analyzed: {sentiment_report.get('data_source_count', 0)}")
        print(f"🔥 Brand Health Score: {sentiment_report.get('summary', {}).get('brand_health_score', 'N/A')}")
        print(f"💪 Overall Sentiment: {sentiment_report.get('summary', {}).get('overall_sentiment', 'N/A')}")
        
        if 'real_metrics' in sentiment_report:
            metrics = sentiment_report['real_metrics']
            print(f"📊 Total Likes: {metrics.get('total_likes', 0):,}")
            print(f"💬 Total Comments: {metrics.get('total_comments', 0):,}")
            print(f"⚡ Avg Likes per Post: {metrics.get('average_likes_per_post', 0):,}")
        
        print(f"\n🎯 Top Insights:")
        insights = sentiment_report.get('insights', [])
        for i, insight in enumerate(insights[:3], 1):
            print(f"   {i}. {insight}")
        
        print(f"\n💡 Top Recommendations:")
        recommendations = sentiment_report.get('recommendations', [])
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec}")
        
        # Generate engagement metrics report
        print("\n📱 Generating Nike Engagement Performance Report...")
        engagement_report = report_openai_service.generate_engagement_metrics_report(project_id=1)
        
        print(f"\n✅ Nike Engagement Analysis Complete!")
        # Use the correct path to get engagement rate
        engagement_rate = 0
        if 'summary' in engagement_report and 'engagement_rates' in engagement_report['summary']:
            eng_rates = engagement_report['summary']['engagement_rates']
            engagement_rate = eng_rates.get('avg_engagement_rate', 0)
        
        print(f"📈 Engagement Rate: {engagement_rate}%")
        print(f"👥 Total Followers: {engagement_report.get('real_metrics', {}).get('total_followers', 100000000):,}")
        
        # Get brand health score
        brand_health = "N/A"
        if 'executive_metrics' in engagement_report:
            exec_metrics = engagement_report['executive_metrics']
            if 'brand_health_scores' in exec_metrics:
                brand_health = exec_metrics['brand_health_scores'].get('overall_health', 'N/A')
        elif 'benchmarks' in engagement_report:
            brand_health = engagement_report['benchmarks'].get('brand_sentiment_score', 'N/A')
            
        print(f"🏆 Brand Health: {brand_health}")
        
        print("\n🎉 Nike Brand Performance Report Test Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error during Nike brand analysis: {str(e)}")
        import traceback
        print(f"📋 Full error details: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_nike_brand_analysis()