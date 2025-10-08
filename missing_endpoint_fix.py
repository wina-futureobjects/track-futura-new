
# Add this to BrightDataScraperRequestViewSet in views.py

@action(detail=False, methods=['post'])
def trigger_scraper(self, request):
    """Trigger BrightData scraper directly - MISSING ENDPOINT FIX"""
    try:
        platform = request.data.get('platform', 'instagram')
        urls = request.data.get('urls', [])
        input_collection_id = request.data.get('input_collection_id')
        
        # Get or create project
        from users.models import Project
        project = Project.objects.first()
        if not project:
            return Response({'error': 'No project found'}, status=400)
        
        # Create batch job
        scraper = BrightDataAutomatedBatchScraper()
        batch_job = scraper.create_batch_job(
            name=f"Direct trigger {timezone.now().strftime('%Y%m%d_%H%M%S')}",
            project_id=project.id,
            source_folder_ids=[],
            platforms_to_scrape=[platform],
            content_types_to_scrape={platform: ['posts']},
            num_of_posts=5
        )
        
        if batch_job:
            # Execute immediately
            success = scraper.execute_batch_job(batch_job.id)
            if success:
                return Response({
                    'message': 'BrightData scraper triggered successfully!',
                    'batch_job_id': batch_job.id,
                    'platform': platform,
                    'status': 'processing'
                })
            else:
                return Response({'error': 'Failed to execute BrightData job'}, status=500)
        else:
            return Response({'error': 'Failed to create BrightData batch job'}, status=500)
            
    except Exception as e:
        logger.error(f"Error triggering scraper: {str(e)}")
        return Response({'error': f'Scraper trigger failed: {str(e)}'}, status=500)
