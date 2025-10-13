#!/usr/bin/env python3
"""
Django Management Command to Import BrightData Files
===================================================
"""
import os
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from core.models import Job, DataStorage, Post

class Command(BaseCommand):
    help = 'Import BrightData scraped Instagram and Facebook files'

    def handle(self, *args, **options):
        self.stdout.write("🚀 BRIGHTDATA SCRAPED FILES IMPORT")
        self.stdout.write("=" * 50)
        
        # File paths
        instagram_file = r"C:\Users\winam\Downloads\bd_20251013_024949_0.json"
        facebook_file = r"C:\Users\winam\Downloads\bd_20251013_024949_0 (1).json"
        
        total_imported = 0
        
        # Import Instagram data
        if os.path.exists(instagram_file):
            instagram_count = self.import_instagram_data(instagram_file)
            total_imported += instagram_count
        else:
            self.stdout.write(f"❌ Instagram file not found: {instagram_file}")
        
        # Import Facebook data  
        if os.path.exists(facebook_file):
            facebook_count = self.import_facebook_data(facebook_file)
            total_imported += facebook_count
        else:
            self.stdout.write(f"❌ Facebook file not found: {facebook_file}")
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(f"🎉 IMPORT COMPLETE: {total_imported} total posts imported")
        self.stdout.write(f"📊 View Instagram: http://localhost:8000/api/run-info/400/")
        self.stdout.write(f"📊 View Facebook: http://localhost:8000/api/run-info/401/")
        self.stdout.write(f"🌐 Frontend (IG): https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/run/400")
        self.stdout.write(f"🌐 Frontend (FB): https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/run/401")

    def import_instagram_data(self, file_path):
        """Import Instagram posts from JSON file"""
        self.stdout.write(f"📱 Importing Instagram data from: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            instagram_posts = json.load(f)
        
        # Create or get job for Instagram import
        job, created = Job.objects.get_or_create(
            id=5,
            defaults={
                'name': f'Instagram Scraped Data Import - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                'description': 'Imported from BrightData scraped files',
                'status': 'completed',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
        )
        
        # Create DataStorage entry for Instagram
        data_storage, created = DataStorage.objects.get_or_create(
            job=job,
            run_id=400,
            defaults={
                'data_type': 'instagram',
                'file_path': f'/data/instagram_scraped_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
                'total_posts': len(instagram_posts),
                'status': 'completed',
                'created_at': datetime.now()
            }
        )
        
        imported_count = 0
        for post_data in instagram_posts:
            try:
                post, created = Post.objects.get_or_create(
                    data_storage=data_storage,
                    post_id=post_data.get('post_id', post_data.get('shortcode', f'unknown_{imported_count}')),
                    defaults={
                        'platform': 'instagram',
                        'user_posted': post_data.get('user_posted', 'unknown'),
                        'description': post_data.get('description', ''),
                        'date_posted': datetime.fromisoformat(post_data.get('timestamp', '2025-10-13T00:00:00.000Z').replace('Z', '+00:00')),
                        'likes': post_data.get('likes', 0),
                        'num_comments': post_data.get('num_comments', 0),
                        'profile_url': post_data.get('profile_url', ''),
                        'post_url': post_data.get('url', ''),
                        'raw_data': json.dumps(post_data)
                    }
                )
                if created:
                    imported_count += 1
                    self.stdout.write(f"✅ Imported Instagram post: {post_data.get('user_posted', 'unknown')} - {post_data.get('description', '')[:50]}...")
            except Exception as e:
                self.stdout.write(f"❌ Error importing Instagram post: {e}")
        
        # Update total posts count
        data_storage.total_posts = imported_count
        data_storage.save()
        
        self.stdout.write(f"📊 Instagram Import Complete: {imported_count} posts imported")
        self.stdout.write(f"📱 Instagram DataStorage ID: {data_storage.id}, Run ID: {data_storage.run_id}")
        return imported_count

    def import_facebook_data(self, file_path):
        """Import Facebook posts from JSON file"""
        self.stdout.write(f"📘 Importing Facebook data from: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            facebook_posts = json.load(f)
        
        # Create or get job for Facebook import
        job, created = Job.objects.get_or_create(
            id=6,
            defaults={
                'name': f'Facebook Scraped Data Import - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                'description': 'Imported from BrightData scraped files',
                'status': 'completed',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
        )
        
        # Create DataStorage entry for Facebook
        data_storage, created = DataStorage.objects.get_or_create(
            job=job,
            run_id=401,
            defaults={
                'data_type': 'facebook',
                'file_path': f'/data/facebook_scraped_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
                'total_posts': len(facebook_posts),
                'status': 'completed',
                'created_at': datetime.now()
            }
        )
        
        imported_count = 0
        for post_data in facebook_posts:
            try:
                post, created = Post.objects.get_or_create(
                    data_storage=data_storage,
                    post_id=post_data.get('post_id', post_data.get('shortcode', f'facebook_unknown_{imported_count}')),
                    defaults={
                        'platform': 'facebook',
                        'user_posted': post_data.get('user_username_raw', 'unknown'),
                        'description': post_data.get('content', ''),
                        'date_posted': datetime.fromisoformat(post_data.get('date_posted', '2025-10-13T00:00:00.000Z').replace('Z', '+00:00')),
                        'likes': post_data.get('likes', post_data.get('num_likes_type', {}).get('num', 0)),
                        'num_comments': post_data.get('num_comments', 0),
                        'profile_url': post_data.get('user_url', ''),
                        'post_url': post_data.get('url', ''),
                        'raw_data': json.dumps(post_data)
                    }
                )
                if created:
                    imported_count += 1
                    self.stdout.write(f"✅ Imported Facebook post: {post_data.get('user_username_raw', 'unknown')} - {post_data.get('content', '')[:50]}...")
            except Exception as e:
                self.stdout.write(f"❌ Error importing Facebook post: {e}")
        
        # Update total posts count
        data_storage.total_posts = imported_count
        data_storage.save()
        
        self.stdout.write(f"📊 Facebook Import Complete: {imported_count} posts imported")
        self.stdout.write(f"📘 Facebook DataStorage ID: {data_storage.id}, Run ID: {data_storage.run_id}")
        return imported_count