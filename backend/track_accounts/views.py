from django.shortcuts import render, get_object_or_404
import csv
import io
import json
import datetime
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse
from django.db.models import Q
from .models import TrackSource, ReportFolder, ReportEntry
from .serializers import (
    TrackSourceSerializer,
    ReportFolderSerializer, ReportEntrySerializer, ReportFolderDetailSerializer
)

class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class that respects the page_size parameter
    """
    page_size = 25  # Default page size
    page_size_query_param = 'page_size'
    max_page_size = 1000
    page_query_param = 'page'

class TrackSourceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Track Sources (formerly Track Accounts)
    """
    serializer_class = TrackSourceSerializer
    permission_classes = [AllowAny]  # For testing, use proper permissions in production
    pagination_class = CustomPageNumberPagination
    
    def get_queryset(self):
        """Filter sources based on query parameters"""
        queryset = TrackSource.objects.all()
        
        # Filter by project if specified
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
            )
        
        # Social media filters
        has_facebook = self.request.query_params.get('has_facebook')
        has_instagram = self.request.query_params.get('has_instagram')
        has_linkedin = self.request.query_params.get('has_linkedin')
        has_tiktok = self.request.query_params.get('has_tiktok')
        
        # Apply social media filters (AND logic - sources must have ALL selected platforms)
        if has_facebook == 'true':
            queryset = queryset.filter(facebook_link__isnull=False).exclude(facebook_link='')
        
        if has_instagram == 'true':
            queryset = queryset.filter(instagram_link__isnull=False).exclude(instagram_link='')
        
        if has_linkedin == 'true':
            queryset = queryset.filter(linkedin_link__isnull=False).exclude(linkedin_link='')
        
        if has_tiktok == 'true':
            queryset = queryset.filter(tiktok_link__isnull=False).exclude(tiktok_link='')
        
        # Date filters
        date_range = self.request.query_params.get('date_range')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        # Apply date filters
        if date_range and date_range != 'all':
            today = datetime.date.today()
            
            if date_range == 'today':
                queryset = queryset.filter(created_at__date=today)
            elif date_range == 'week':
                week_ago = today - datetime.timedelta(days=7)
                queryset = queryset.filter(created_at__date__gte=week_ago, created_at__date__lte=today)
            elif date_range == 'month':
                month_ago = today - datetime.timedelta(days=30)
                queryset = queryset.filter(created_at__date__gte=month_ago, created_at__date__lte=today)
            elif date_range == 'year':
                year_ago = today - datetime.timedelta(days=365)
                queryset = queryset.filter(created_at__date__gte=year_ago, created_at__date__lte=today)
        
        # Custom date range
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        print(f"=== BACKEND FILTER DEBUG ===")
        print(f"Project ID: {project_id}")
        print(f"Search: {search}")
        print(f"Has Facebook: {has_facebook}")
        print(f"Has Instagram: {has_instagram}")
        print(f"Has LinkedIn: {has_linkedin}")
        print(f"Has TikTok: {has_tiktok}")
        print(f"Date Range: {date_range}")
        print(f"Start Date: {start_date}")
        print(f"End Date: {end_date}")
        print(f"Page: {self.request.query_params.get('page')}")
        print(f"Page Size: {self.request.query_params.get('page_size')}")
        print(f"Final queryset count: {queryset.count()}")
        print(f"=== END BACKEND FILTER DEBUG ===")
        
        return queryset.order_by('name')
    
    def perform_create(self, serializer):
        """
        Set project when creating a new source
        """
        # Get project from request data directly
        project_id = self.request.data.get('project')
        serializer.save(project_id=project_id)
    
    def perform_update(self, serializer):
        """
        Update project when updating source if needed
        """
        # Get project from request data directly
        project_id = self.request.data.get('project')
        serializer.save(project_id=project_id)

    def destroy(self, request, *args, **kwargs):
        """
        Custom destroy method to handle deletion with proper logging
        """
        try:
            instance = self.get_object()
            print(f"Attempting to delete TrackSource: {instance.id} - {instance.name}")
            
            # Perform the deletion
            self.perform_destroy(instance)
            
            print(f"Successfully deleted TrackSource: {instance.id} - {instance.name}")
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            print(f"Error deleting TrackSource: {str(e)}")
            return Response(
                {'error': f'Failed to delete source: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['POST'])
    def upload_csv(self, request):
        """
        Upload CSV file and parse the track source data
        """
        try:
            csv_file = request.FILES.get('file')
            if not csv_file:
                return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not csv_file.name.endswith('.csv'):
                return Response({'error': 'File must be a CSV'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get project ID and validate it
            project_id = request.data.get('project')
            if not project_id:
                return Response({'error': 'Project ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                project_id = int(project_id)
            except (ValueError, TypeError):
                return Response({'error': 'Invalid project ID'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify project exists
            from users.models import Project
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                return Response({'error': f'Project with ID {project_id} does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Read the CSV file
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            # Lists to track created and updated objects
            created_objects = []
            updated_objects = []
            
            # Process each row
            for row in reader:
                # Check if the row has the required data (only name is required now)
                if not row.get('Name'):
                    continue
                
                # Prepare the data dictionary with project_id instead of project
                data = {
                    'name': row.get('Name', '').strip(),
                    'facebook_link': row.get('FACEBOOK_LINK', '').strip() or None,
                    'instagram_link': row.get('INSTAGRAM_LINK', '').strip() or None,
                    'linkedin_link': row.get('LINKEDIN_LINK', '').strip() or None,
                    'tiktok_link': row.get('TIKTOK_LINK', '').strip() or None,
                    'other_social_media': row.get('OTHER_SOCIAL_MEDIA', '').strip() or None,
                    'project_id': project_id  # Use project_id instead of project
                }
                
                # Check if source with this name already exists in the project
                existing_source = TrackSource.objects.filter(
                    name=data['name'], 
                    project_id=project_id
                ).first()
                
                if existing_source:
                    # Update existing source
                    for key, value in data.items():
                        if key != 'project_id':  # Don't change project_id
                            setattr(existing_source, key, value)
                    existing_source.save()
                    updated_objects.append(existing_source)
                else:
                    # Create new source
                    new_source = TrackSource.objects.create(**data)
                    created_objects.append(new_source)
            
            return Response({
                'message': f'Successfully processed CSV. Created: {len(created_objects)}, Updated: {len(updated_objects)}',
                'created': len(created_objects),
                'updated': len(updated_objects)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def download_csv(self, request):
        """
        Download track sources as CSV with proper formatting
        """
        try:
            # Get query parameters for filtering
            project_id = request.query_params.get('project')
            
            # Start with base queryset
            queryset = TrackSource.objects.all()
            
            # Filter by project if specified
            if project_id:
                queryset = queryset.filter(project_id=project_id)
            
            # Apply the same filters as the list view
            search = request.query_params.get('search')
            if search:
                queryset = queryset.filter(Q(name__icontains=search))
            
            # Social media filters
            has_facebook = request.query_params.get('has_facebook')
            has_instagram = request.query_params.get('has_instagram')
            has_linkedin = request.query_params.get('has_linkedin')
            has_tiktok = request.query_params.get('has_tiktok')
            
            if has_facebook == 'true':
                queryset = queryset.filter(facebook_link__isnull=False).exclude(facebook_link='')
            if has_instagram == 'true':
                queryset = queryset.filter(instagram_link__isnull=False).exclude(instagram_link='')
            if has_linkedin == 'true':
                queryset = queryset.filter(linkedin_link__isnull=False).exclude(linkedin_link='')
            if has_tiktok == 'true':
                queryset = queryset.filter(tiktok_link__isnull=False).exclude(tiktok_link='')
            
            # Create CSV response with proper encoding
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename="track_sources_export.csv"'
            
            # Use DictWriter for better handling of special characters
            fieldnames = [
                'ID',
                'Name', 
                'Facebook Link',
                'Instagram Link', 
                'LinkedIn Link', 
                'TikTok Link',
                'Additional Links',
                'Project ID',
                'Created Date',
                'Last Updated'
            ]
            
            writer = csv.DictWriter(response, fieldnames=fieldnames)
            
            # Write export metadata as comments (some CSV readers support this)
            writer.writerow({'ID': '# Track Sources Export'})
            writer.writerow({'ID': f'# Export Date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'})
            writer.writerow({'ID': f'# Total Records: {queryset.count()}'})
            if project_id:
                writer.writerow({'ID': f'# Project ID: {project_id}'})
            if search:
                writer.writerow({'ID': f'# Search Filter: {search}'})
            if any([has_facebook == 'true', has_instagram == 'true', has_linkedin == 'true', has_tiktok == 'true']):
                filters = []
                if has_facebook == 'true': filters.append('Facebook')
                if has_instagram == 'true': filters.append('Instagram')
                if has_linkedin == 'true': filters.append('LinkedIn')
                if has_tiktok == 'true': filters.append('TikTok')
                writer.writerow({'ID': f'# Social Media Filters: {", ".join(filters)}'})
            writer.writerow({'ID': ''})  # Empty row for separation
            
            writer.writeheader()
            
            # Write data rows
            for source in queryset:
                writer.writerow({
                    'ID': source.id,
                    'Name': source.name,
                    'Facebook Link': source.facebook_link or '',
                    'Instagram Link': source.instagram_link or '',
                    'LinkedIn Link': source.linkedin_link or '',
                    'TikTok Link': source.tiktok_link or '',
                    'Additional Links': source.other_social_media or '',
                    'Project ID': source.project.id if source.project else '',
                    'Created Date': source.created_at.strftime('%Y-%m-%d %H:%M:%S') if source.created_at else '',
                    'Last Updated': source.updated_at.strftime('%Y-%m-%d %H:%M:%S') if source.updated_at else '',
                })
            
            return response
            
        except Exception as e:
            print(f"CSV export error: {str(e)}")
            return Response({'error': f'Failed to export CSV: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def statistics(self, request):
        """
        Get statistics for filtering
        """
        try:
            # Get query parameters
            project_id = request.query_params.get('project')
            
            # Start with base queryset
            queryset = TrackSource.objects.all()
            
            # Filter by project if specified
            if project_id:
                queryset = queryset.filter(project_id=project_id)
            
            # Calculate statistics
            total = queryset.count()
            
            # Social media counts
            social_media_counts = {
                'facebook': queryset.exclude(
                    Q(facebook_link__isnull=True) | Q(facebook_link='')
                ).count(),
                'instagram': queryset.exclude(
                    Q(instagram_link__isnull=True) | Q(instagram_link='')
                ).count(),
                'linkedin': queryset.exclude(
                    Q(linkedin_link__isnull=True) | Q(linkedin_link='')
                ).count(),
                'tiktok': queryset.exclude(
                    Q(tiktok_link__isnull=True) | Q(tiktok_link='')
                ).count(),
            }
            
            return Response({
                'total': total,
                'socialMediaCounts': social_media_counts,
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ReportFolderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing generated reports
    """
    queryset = ReportFolder.objects.all()
    serializer_class = ReportFolderSerializer
    permission_classes = [AllowAny]  # For testing, use proper permissions in production
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ReportFolderDetailSerializer
        return self.serializer_class
    
    def create(self, request, *args, **kwargs):
        """
        Custom create method to handle validation errors better
        """
        try:
            # Validate required fields
            if not request.data.get('name'):
                return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not request.data.get('start_date'):
                return Response({'error': 'Start date is required'}, status=status.HTTP_400_BAD_REQUEST)
                
            if not request.data.get('end_date'):
                return Response({'error': 'End date is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create serializer with data
            serializer = self.get_serializer(data=request.data)
            
            # If serializer validation fails, return detailed errors
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Save the instance
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except Exception as e:
            print(f"Error creating report folder: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def _find_matching_source(self, username):
        """Find matching TrackSource by Instagram username"""
        if not username:
            return None
        
        # Normalize the username input
        normalized_username = username.lower().strip() if username else ''
        if not normalized_username:
            return None
            
        # Debug
        print(f"Looking for match for Instagram username: '{normalized_username}'")
        
        # MATCHING STRATEGY: Extract username from instagram_link URL and compare
        try:
            # Query sources with instagram_link that's not null/empty
            sources = TrackSource.objects.exclude(instagram_link__isnull=True).exclude(instagram_link='')
            
            for source in sources:
                try:
                    # Extract username from instagram_link URL
                    import re
                    url_pattern = r'(?:https?:\/\/)?(?:www\.)?instagram\.com\/([^\/\?]+)'
                    matches = re.search(url_pattern, source.instagram_link)
                    if matches:
                        extracted_username = matches.group(1).lower().strip()
                        if extracted_username == normalized_username:
                            print(f"Found URL match with instagram_link: {source.name} (ID: {source.id})")
                            return source
                except Exception as e:
                    print(f"Error processing source {source.id}: {str(e)}")
                    continue
        except Exception as e:
            print(f"Error during URL extraction match: {str(e)}")
            
        # No matches found
        print(f"No matching source found for username: '{normalized_username}'")
        return None

    def _find_matching_facebook_source(self, user_url):
        """Find matching TrackSource by Facebook user_url"""
        if not user_url:
            return None
        
        # Normalize the user_url input
        normalized_user_url = user_url.lower().strip() if user_url else ''
        if not normalized_user_url:
            return None
            
        # Debug
        print(f"Looking for match for Facebook user_url: '{normalized_user_url}'")
        
        # MATCHING STRATEGY: Direct exact match with facebook_link
        try:
            # Direct match with facebook_link field
            source = TrackSource.objects.filter(facebook_link__iexact=normalized_user_url).first()
            if source:
                print(f"Found direct match with facebook_link: {source.name} (ID: {source.id})")
                return source
        except Exception as e:
            print(f"Error during direct user_url match: {str(e)}")
        
        # No matches found
        print(f"No matching source found for user_url: '{normalized_user_url}'")
        return None 

# Keep backward compatibility alias
TrackAccountViewSet = TrackSourceViewSet 