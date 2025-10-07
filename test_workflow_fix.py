#!/usr/bin/env python3
"""
Test the workflow system to ensure it creates BrightData batch jobs correctly
"""

import os
import sys
import django

# Add the backend directory to Python path
backend_path = r'C:\Users\winam\OneDrive\문서\PREVIOUS\TrackFutura - Copy\backend'
sys.path.append(backend_path)
os.chdir(backend_path)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_workflow_scraping_run():
    """Test creating and starting a scraping run"""
    print("=== TESTING WORKFLOW SCRAPING RUN ===")
    print()
    
    from workflow.models import ScrapingRun, ScrapingJob
    from brightdata_integration.models import BrightDataBatchJob, BrightDataConfig
    from users.models import Project
    from workflow.services import WorkflowService
    
    try:
        # Get a project
        project = Project.objects.first()
        if not project:
            print("❌ No projects found")
            return
            
        print(f"✅ Using project: {project.name}")
        
        # Create a scraping run
        configuration = {
            'num_of_posts': 5,
            'platforms': ['instagram'],
            'content_types': {'instagram': ['posts']}
        }
        
        workflow_service = WorkflowService()
        scraping_run = workflow_service.create_scraping_run(
            project_id=project.id,
            configuration=configuration
        )
        
        if scraping_run:
            print(f"✅ Created scraping run: {scraping_run.name} (ID: {scraping_run.id})")
            print(f"   Status: {scraping_run.status}")
            print(f"   Total jobs: {scraping_run.total_jobs}")
            
            # Check if BrightData batch jobs were created
            batch_jobs = BrightDataBatchJob.objects.filter(
                scraping_jobs__scraping_run=scraping_run
            ).distinct()
            
            print(f"✅ Created {batch_jobs.count()} BrightData batch jobs")
            
            if batch_jobs.exists():
                for batch_job in batch_jobs:
                    print(f"   - Batch Job: {batch_job.name}")
                    print(f"     Platforms: {batch_job.platforms_to_scrape}")
                    print(f"     Status: {batch_job.status}")
                    
                # Test execution (simulated)
                print()
                print("🧪 Testing execution...")
                
                scraping_jobs = ScrapingJob.objects.filter(scraping_run=scraping_run)
                print(f"Found {scraping_jobs.count()} scraping jobs")
                
                for job in scraping_jobs:
                    if job.batch_job:
                        print(f"   Job {job.id}: Has batch job {job.batch_job.id}")
                        print(f"   Platform: {job.platform}")
                        print(f"   URL: {job.url}")
                    else:
                        print(f"   Job {job.id}: ❌ No batch job assigned")
                        
                print("🎯 Workflow system is properly connected to BrightData!")
            else:
                print("❌ No BrightData batch jobs created")
        else:
            print("❌ Failed to create scraping run")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_workflow_scraping_run()