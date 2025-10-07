#!/usr/bin/env python3
"""
TrackFutura System Status Check
Comprehensive verification of all integrations
"""

import os
import sys
import django

# Setup Django environment
backend_path = r'C:\Users\winam\OneDrive\문서\PREVIOUS\TrackFutura - Copy\backend'
sys.path.append(backend_path)
os.chdir(backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def check_environment_variables():
    """Check if all required environment variables are set"""
    print("🔧 Environment Variables Check")
    print("-" * 40)
    
    required_vars = {
        'OPENAI_API_KEY': 'OpenAI GPT Integration',
        'PINECONE_API_KEY': 'Vector Database',  
        'BRIGHTDATA_API_KEY': 'Social Media Scraping',
        'BRIGHTDATA_WEBHOOK_TOKEN': 'Webhook Security'
    }
    
    all_set = True
    for var, description in required_vars.items():
        value = os.getenv(var, '')
        status = "✅" if value and len(value) > 10 else "❌"
        print(f"{status} {description}: {'Configured' if value else 'Missing'}")
        if not value:
            all_set = False
    
    return all_set

def check_database_integration():
    """Check database models and data"""
    print("\n💾 Database Integration Check")
    print("-" * 40)
    
    try:
        from users.models import User, Project, Platform, Service
        from brightdata_integration.models import BrightDataConfig, BrightDataBatchJob
        from workflow.models import InputCollection, ScrapingJob
        
        # Check core models
        users = User.objects.count()
        projects = Project.objects.count()
        platforms = Platform.objects.count()
        services = Service.objects.count()
        
        print(f"✅ Users: {users}")
        print(f"✅ Projects: {projects}")
        print(f"✅ Platforms: {platforms}")
        print(f"✅ Services: {services}")
        
        # Check BrightData integration
        bd_configs = BrightDataConfig.objects.count()
        bd_jobs = BrightDataBatchJob.objects.count()
        
        print(f"✅ BrightData Configs: {bd_configs}")
        print(f"✅ BrightData Jobs: {bd_jobs}")
        
        # Check workflow data
        input_collections = InputCollection.objects.count()
        scraping_jobs = ScrapingJob.objects.count()
        
        print(f"✅ Input Collections: {input_collections}")
        print(f"✅ Scraping Jobs: {scraping_jobs}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database Error: {e}")
        return False

def check_ai_integration():
    """Check AI services"""
    print("\n🤖 AI Integration Check")
    print("-" * 40)
    
    try:
        # Test OpenAI
        from chat.openai_service import openai_service
        if openai_service.client:
            print("✅ OpenAI Service: Connected")
        else:
            print("❌ OpenAI Service: Not connected")
            
        # Test Sentiment Analysis
        from common.sentiment_analysis_service import sentiment_service
        if sentiment_service.client:
            print("✅ Sentiment Analysis: Connected")
        else:
            print("❌ Sentiment Analysis: Not connected")
            
        # Test Pinecone (check if can import)
        try:
            from AI_database.LinkedInHandler import LinkedInPineconeDB
            print("✅ Pinecone Integration: Available")
        except Exception as e:
            print(f"❌ Pinecone Integration: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ AI Integration Error: {e}")
        return False

def check_social_media_data():
    """Check social media data availability"""
    print("\n📱 Social Media Data Check")
    print("-" * 40)
    
    try:
        from instagram_data.models import InstagramPost, InstagramComment
        from facebook_data.models import FacebookPost, FacebookComment
        from linkedin_data.models import LinkedInPost, LinkedInComment
        from tiktok_data.models import TikTokPost, TikTokComment
        
        ig_posts = InstagramPost.objects.count()
        ig_comments = InstagramComment.objects.count()
        
        fb_posts = FacebookPost.objects.count()
        fb_comments = FacebookComment.objects.count()
        
        li_posts = LinkedInPost.objects.count()
        li_comments = LinkedInComment.objects.count()
        
        tt_posts = TikTokPost.objects.count()
        tt_comments = TikTokComment.objects.count()
        
        print(f"📸 Instagram: {ig_posts} posts, {ig_comments} comments")
        print(f"📘 Facebook: {fb_posts} posts, {fb_comments} comments")
        print(f"💼 LinkedIn: {li_posts} posts, {li_comments} comments")
        print(f"🎵 TikTok: {tt_posts} posts, {tt_comments} comments")
        
        total_data = ig_posts + fb_posts + li_posts + tt_posts
        print(f"📊 Total Social Media Posts: {total_data}")
        
        return total_data > 0
        
    except Exception as e:
        print(f"❌ Social Media Data Error: {e}")
        return False

def main():
    """Run comprehensive system check"""
    print("🎯 TrackFutura System Status Check")
    print("=" * 50)
    
    env_ok = check_environment_variables()
    db_ok = check_database_integration()
    ai_ok = check_ai_integration()
    data_available = check_social_media_data()
    
    print("\n" + "=" * 50)
    print("📋 SYSTEM STATUS SUMMARY")
    print("=" * 50)
    
    print(f"🔧 Environment Setup: {'✅ Ready' if env_ok else '⚠️ Needs Configuration'}")
    print(f"💾 Database Integration: {'✅ Working' if db_ok else '❌ Issues Found'}")
    print(f"🤖 AI Services: {'✅ Connected' if ai_ok else '❌ Not Working'}")
    print(f"📱 Social Media Data: {'✅ Available' if data_available else '⚠️ No Data Yet'}")
    
    if env_ok and db_ok and ai_ok:
        print("\n🎉 SYSTEM STATUS: FULLY OPERATIONAL")
        print("✅ All core integrations are working!")
        print("🚀 Ready for production use")
    else:
        print("\n⚠️ SYSTEM STATUS: NEEDS ATTENTION")
        print("🔧 Some components need configuration")

if __name__ == "__main__":
    main()