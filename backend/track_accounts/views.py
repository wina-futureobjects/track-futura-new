from django.shortcuts import render, get_object_or_404
import csv
import io
import json
import datetime
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from django.db.models import Q
from .models import TrackAccount, ReportFolder, ReportEntry
from .serializers import (
    TrackAccountSerializer,
    ReportFolderSerializer, ReportEntrySerializer, ReportFolderDetailSerializer
)

class TrackAccountViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Track Accounts
    """
    serializer_class = TrackAccountSerializer
    permission_classes = [AllowAny]  # For testing, use proper permissions in production
    
    def get_queryset(self):
        """
        Get queryset with filtering options
        """
        queryset = TrackAccount.objects.all()
        
        # Get query parameters
        project_id = self.request.query_params.get('project')
        search = self.request.query_params.get('search')
        risk_classification = self.request.query_params.get('risk_classification')
        close_monitoring = self.request.query_params.get('close_monitoring')
        has_facebook = self.request.query_params.get('has_facebook')
        has_instagram = self.request.query_params.get('has_instagram')
        has_linkedin = self.request.query_params.get('has_linkedin')
        has_tiktok = self.request.query_params.get('has_tiktok')
        
        # Filter by project if specified
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by search term if provided
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(iac_no__icontains=search)
            )
        
        # Filter by risk classification if provided
        if risk_classification:
            queryset = queryset.filter(risk_classification=risk_classification)
        
        # Filter by close monitoring if provided
        if close_monitoring is not None:
            if close_monitoring.lower() == 'true':
                queryset = queryset.filter(close_monitoring=True)
            elif close_monitoring.lower() == 'false':
                queryset = queryset.filter(close_monitoring=False)
                
        # Filter by social media presence
        if has_facebook:
            queryset = queryset.exclude(
                Q(facebook_link__isnull=True) | Q(facebook_link='')
            )
        
        if has_instagram:
            queryset = queryset.exclude(
                Q(instagram_link__isnull=True) | Q(instagram_link='')
            )
            
        if has_linkedin:
            queryset = queryset.exclude(
                Q(linkedin_link__isnull=True) | Q(linkedin_link='')
            )
            
        if has_tiktok:
            queryset = queryset.exclude(
                Q(tiktok_link__isnull=True) | Q(tiktok_link='')
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Set project when creating a new account
        """
        # Get project from request data directly
        project_id = self.request.data.get('project')
        serializer.save(project_id=project_id)
    
    def perform_update(self, serializer):
        """
        Update project when updating account if needed
        """
        # Get project from request data directly
        project_id = self.request.data.get('project')
        serializer.save(project_id=project_id)

    @action(detail=False, methods=['POST'])
    def upload_csv(self, request):
        """
        Upload CSV file and parse the track account data
        """
        try:
            csv_file = request.FILES.get('file')
            if not csv_file:
                return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not csv_file.name.endswith('.csv'):
                return Response({'error': 'File must be a CSV'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get project ID directly from request data
            project_id = request.data.get('project')
            
            # Read the CSV file
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            # Lists to track created and updated objects
            created_objects = []
            updated_objects = []
            
            # Process each row
            for row in reader:
                # Check if the row has the required data
                if not row.get('Name') or not row.get('IAC_NO'):
                    continue
                
                # Prepare the data dictionary
                data = {
                    'name': row.get('Name', '').strip(),
                    'iac_no': row.get('IAC_NO', '').strip(),
                    'facebook_link': row.get('FACEBOOK_LINK', '').strip() or None,
                    'instagram_link': row.get('INSTAGRAM_LINK', '').strip() or None,
                    'linkedin_link': row.get('LINKEDIN_LINK', '').strip() or None,
                    'tiktok_link': row.get('TIKTOK_LINK', '').strip() or None,
                    'other_social_media': row.get('OTHER_SOCIAL_MEDIA', '').strip() or None,
                    'risk_classification': row.get('RISK_CLASSIFICATION', '').strip() or None,
                    'close_monitoring': row.get('CLOSE_MONITORING', '').strip().lower() in ['yes', 'true', '1'],
                    'posting_frequency': row.get('POSTING_FREQUENCY', '').strip() or None,
                    'project': project_id
                }
                
                # Check if account with this IAC_NO already exists
                existing_account = TrackAccount.objects.filter(iac_no=data['iac_no']).first()
                
                if existing_account:
                    # Update existing account
                    for key, value in data.items():
                        if key != 'project':  # Don't change project
                            setattr(existing_account, key, value)
                    existing_account.save()
                    updated_objects.append(existing_account)
                else:
                    # Create new account
                    new_account = TrackAccount.objects.create(**data)
                    created_objects.append(new_account)
            
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
        Download track accounts as CSV
        """
        try:
            # Get query parameters for filtering
            project_id = request.query_params.get('project')
            
            # Start with base queryset
            queryset = TrackAccount.objects.all()
            
            # Filter by project if specified
            if project_id:
                queryset = queryset.filter(project_id=project_id)
            
            # Create CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="track_accounts.csv"'
            
            writer = csv.writer(response)
            
            # Write header
            writer.writerow([
                'Name', 'IAC_NO', 
                'FACEBOOK_LINK', 'INSTAGRAM_LINK', 'LINKEDIN_LINK', 'TIKTOK_LINK',
                'OTHER_SOCIAL_MEDIA', 'RISK_CLASSIFICATION', 'CLOSE_MONITORING', 'POSTING_FREQUENCY'
            ])
            
            # Write data rows
            for account in queryset:
                writer.writerow([
                    account.name,
                    account.iac_no,
                    account.facebook_link or '',
                    account.instagram_link or '',
                    account.linkedin_link or '',
                    account.tiktok_link or '',
                    account.other_social_media or '',
                    account.risk_classification or '',
                    'Yes' if account.close_monitoring else 'No',
                    account.posting_frequency or ''
                ])
            
            return response
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        """
        Get statistics for filtering
        """
        try:
            # Get query parameters
            project_id = request.query_params.get('project')
            
            # Start with base queryset
            queryset = TrackAccount.objects.all()
            
            # Filter by project if specified
            if project_id:
                queryset = queryset.filter(project_id=project_id)
            
            # Calculate statistics
            total = queryset.count()
            
            # Risk classification counts
            risk_counts = {
                'low': queryset.filter(risk_classification='Low').count(),
                'medium': queryset.filter(risk_classification='Medium').count(),
                'high': queryset.filter(risk_classification='High').count(),
                'critical': queryset.filter(risk_classification='Critical').count(),
            }
            
            # Monitoring counts
            monitoring_counts = {
                'monitored': queryset.filter(close_monitoring=True).count(),
                'unmonitored': queryset.filter(close_monitoring=False).count(),
            }
            
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
                'riskCounts': risk_counts,
                'monitoringCounts': monitoring_counts,
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
    
    def _find_matching_account(self, username):
        """Find matching TrackAccount by Instagram username"""
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
            # Query accounts with instagram_link that's not null/empty
            accounts = TrackAccount.objects.exclude(instagram_link__isnull=True).exclude(instagram_link='')
            
            for account in accounts:
                try:
                    # Extract username from instagram_link URL
                    import re
                    url_pattern = r'(?:https?:\/\/)?(?:www\.)?instagram\.com\/([^\/\?]+)'
                    matches = re.search(url_pattern, account.instagram_link)
                    if matches:
                        extracted_username = matches.group(1).lower().strip()
                        if extracted_username == normalized_username:
                            print(f"Found URL match with instagram_link: {account.name} (ID: {account.id})")
                            return account
                except Exception as e:
                    print(f"Error processing account {account.id}: {str(e)}")
                    continue
        except Exception as e:
            print(f"Error during URL extraction match: {str(e)}")
            
        # No matches found
        print(f"No matching account found for username: '{normalized_username}'")
        return None

    def _find_matching_facebook_account(self, user_url):
        """Find matching TrackAccount by Facebook user_url"""
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
            account = TrackAccount.objects.filter(facebook_link__iexact=normalized_user_url).first()
            if account:
                print(f"Found direct match with facebook_link: {account.name} (ID: {account.id})")
                return account
        except Exception as e:
            print(f"Error during direct user_url match: {str(e)}")
        
        # No matches found
        print(f"No matching account found for user_url: '{normalized_user_url}'")
        return None 