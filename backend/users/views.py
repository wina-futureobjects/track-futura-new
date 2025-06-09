from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from .serializers import (
    UserSerializer, RegisterSerializer, UserProfileSerializer,
    ProjectSerializer, ProjectDetailSerializer,
    OrganizationSerializer, OrganizationDetailSerializer,
    OrganizationMembershipSerializer
)
from .models import UserProfile, Project, Organization, OrganizationMembership
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import NotFound, PermissionDenied
from django.db import models
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.http import JsonResponse

# Create your views here.

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token.key
        })

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        try:
            return UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            # If profile doesn't exist, create one
            return UserProfile.objects.create(user=self.request.user)

# Organization Views
class OrganizationListCreateView(generics.ListCreateAPIView):
    """
    List all organizations user has access to or create a new organization
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        """Get organizations where user is owner or member"""
        user = self.request.user
        return Organization.objects.filter(members=user)

    def perform_create(self, serializer):
        """Create organization and add creator as owner and admin member"""
        organization = serializer.save(owner=self.request.user)
        # Add creator as admin
        OrganizationMembership.objects.create(
            user=self.request.user,
            organization=organization,
            role='admin'
        )

class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an organization
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrganizationDetailSerializer

    def get_queryset(self):
        user = self.request.user
        return Organization.objects.filter(members=user)

    def get_object(self):
        obj = super().get_object()

        # Only owner or admin can update/delete
        if self.request.method != 'GET':
            membership = OrganizationMembership.objects.filter(
                user=self.request.user,
                organization=obj
            ).first()

            if obj.owner != self.request.user and (not membership or membership.role != 'admin'):
                raise PermissionDenied("You don't have permission to modify this organization")

        return obj

class OrganizationStatsView(APIView):
    """
    Get statistics for an organization
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, organization_id, format=None):
        try:
            # Check if user has access to the organization
            organization = Organization.objects.get(id=organization_id)
            if not organization.members.filter(id=request.user.id).exists():
                raise PermissionDenied("You don't have access to this organization")

            # Calculate statistics
            total_members = organization.members.count()
            total_projects = Project.objects.filter(organization=organization).count()

            # Get user's other organizations count
            user_organizations = Organization.objects.filter(members=request.user).exclude(id=organization_id).count()

            stats = {
                'totalMembers': total_members,
                'totalProjects': total_projects,
                'organizations': user_organizations + 1  # Include current organization
            }

            return Response(stats)

        except Organization.DoesNotExist:
            raise NotFound("Organization not found")

class OrganizationMembershipView(generics.ListCreateAPIView):
    """
    List members of an organization or add new members
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrganizationMembershipSerializer

    def get_queryset(self):
        """Get members for a specific organization"""
        organization_id = self.kwargs.get('organization_id')
        try:
            organization = Organization.objects.get(id=organization_id)

            # Check if user has access to this organization
            if not OrganizationMembership.objects.filter(
                user=self.request.user,
                organization=organization
            ).exists():
                raise PermissionDenied("You don't have access to this organization")

            return OrganizationMembership.objects.filter(organization=organization)
        except Organization.DoesNotExist:
            raise NotFound("Organization not found")

    def perform_create(self, serializer):
        """Add member to organization"""
        organization_id = self.kwargs.get('organization_id')
        try:
            organization = Organization.objects.get(id=organization_id)

            # Check if user is owner or admin
            membership = OrganizationMembership.objects.filter(
                user=self.request.user,
                organization=organization
            ).first()

            if organization.owner != self.request.user and (not membership or membership.role != 'admin'):
                raise PermissionDenied("Only organization owners and admins can add members")

            serializer.save(organization=organization)
        except Organization.DoesNotExist:
            raise NotFound("Organization not found")

class OrganizationMembershipDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete organization membership
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrganizationMembershipSerializer

    def get_queryset(self):
        organization_id = self.kwargs.get('organization_id')
        return OrganizationMembership.objects.filter(organization_id=organization_id)

    def get_object(self):
        obj = super().get_object()

        # Check if user has permission (owner or admin)
        if self.request.method != 'GET':
            membership = OrganizationMembership.objects.filter(
                user=self.request.user,
                organization=obj.organization,
                role='admin'
            ).first()

            if obj.organization.owner != self.request.user and not membership:
                raise PermissionDenied("Only organization owners and admins can modify memberships")

            # Don't allow removing the owner's admin role
            if obj.user == obj.organization.owner and self.request.method == 'DELETE':
                raise PermissionDenied("Cannot remove the organization owner")

        return obj

class UserSearchView(generics.ListAPIView):
    """
    Search for users by email
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        email = self.request.query_params.get('email', '')
        if not email:
            return User.objects.none()

        return User.objects.filter(email__iexact=email)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Return just the first match if found (email should be unique)
        user = queryset.first()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

class ProjectListCreateView(generics.ListCreateAPIView):
    """
    List all projects user has access to or create a new project
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        """
        Get projects where:
        1. User is the owner, or
        2. User is an admin/member of the organization and project is public, or
        3. User is specifically authorized for the project
        """
        user = self.request.user

        # Filter by organization if specified
        organization_id = self.request.query_params.get('organization')

        if organization_id:
            # Verify user has access to the organization
            try:
                org = Organization.objects.get(id=organization_id)
                if not org.members.filter(id=user.id).exists():
                    return Project.objects.none()  # No access to this organization

                # Find all projects in this organization that user can access
                own_projects = Project.objects.filter(organization=org, owner=user)

                # Get user's role in this organization
                membership = OrganizationMembership.objects.filter(
                    user=user,
                    organization=org
                ).first()

                # Admin can see all projects in the organization
                if membership and membership.role == 'admin':
                    return Project.objects.filter(organization=org)

                # Regular members can see public projects or ones they're authorized for
                return Project.objects.filter(
                    organization=org
                ).filter(
                    models.Q(owner=user) |
                    models.Q(is_public=True) |
                    models.Q(authorized_users=user)
                ).distinct()
            except Organization.DoesNotExist:
                return Project.objects.none()

        # No organization specified, return all accessible projects across all organizations
        return Project.objects.filter(
            models.Q(owner=user) |
            models.Q(is_public=True, organization__members=user) |
            models.Q(authorized_users=user)
        ).distinct()

    def perform_create(self, serializer):
        """Create project in specified organization"""
        organization_id = serializer.validated_data.get('organization').id

        try:
            organization = Organization.objects.get(id=organization_id)

            # Check if user is a member of this organization
            if not organization.members.filter(id=self.request.user.id).exists():
                raise PermissionDenied("You are not a member of this organization")

            # Check if user has permission to create projects (owner or admin)
            membership = OrganizationMembership.objects.filter(
                user=self.request.user,
                organization=organization
            ).first()

            if organization.owner != self.request.user and (not membership or membership.role != 'admin'):
                raise PermissionDenied("Only organization owners and admins can create projects")

            serializer.save(owner=self.request.user)
        except Organization.DoesNotExist:
            raise NotFound("Organization not found")

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a project
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectDetailSerializer

    def get_queryset(self):
        user = self.request.user

        # Get all potentially accessible projects
        return Project.objects.filter(
            models.Q(owner=user) |
            models.Q(is_public=True, organization__members=user) |
            models.Q(authorized_users=user)
        ).distinct()

    def get_object(self):
        obj = super().get_object()

        # For operations other than GET, verify user has edit permissions
        if self.request.method != 'GET':
            # Owner can always edit
            if obj.owner == self.request.user:
                return obj

            # Check if user is organization admin
            membership = OrganizationMembership.objects.filter(
                user=self.request.user,
                organization=obj.organization,
                role='admin'
            ).first()

            if not membership:
                raise PermissionDenied("You don't have permission to modify this project")

        return obj

@method_decorator(ensure_csrf_cookie, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class CSRFTokenView(APIView):
    """
    Provide CSRF token for frontend applications
    Ultra-permissive for deployment compatibility
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        """Return CSRF token"""
        from django.middleware.csrf import get_token

        try:
            csrf_token = get_token(request)
            return JsonResponse({
                'csrfToken': csrf_token,
                'success': True,
                'message': 'CSRF token generated successfully'
            })
        except Exception as e:
            # Even if CSRF fails, return a fallback
            return JsonResponse({
                'csrfToken': 'fallback-token',
                'success': True,
                'message': f'Fallback token provided: {str(e)}'
            })

    def post(self, request, format=None):
        """Accept POST requests and return token"""
        return self.get(request, format)
