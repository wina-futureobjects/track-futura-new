from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, Project, Organization, OrganizationMembership, UserRole, Platform, Service, PlatformService, Company, UnifiedUserRecord

class UserRoleSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = UserRole
        fields = ['role', 'role_display']
        read_only_fields = ['role_display']

class UserSerializer(serializers.ModelSerializer):
    global_role = UserRoleSerializer(read_only=True)
    company_name = serializers.SerializerMethodField()
    company_id = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'global_role', 'is_active', 'company_name', 'company_id', 'date_joined']
        read_only_fields = ['id', 'global_role', 'company_name', 'company_id', 'date_joined']
        # Explicitly exclude first_name and last_name fields
        extra_kwargs = {
            'first_name': {'write_only': False, 'read_only': True},
            'last_name': {'write_only': False, 'read_only': True}
        }
    
    def get_company_name(self, obj):
        try:
            if hasattr(obj, 'profile') and obj.profile and obj.profile.company:
                return obj.profile.company.name
        except Exception:
            pass
        return None
    
    def get_company_id(self, obj):
        try:
            if hasattr(obj, 'profile') and obj.profile and obj.profile.company:
                return obj.profile.company.id
        except Exception:
            pass
        return None

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    company_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'avatar', 'company', 'company_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'company_name']
    
    def get_company_name(self, obj):
        return obj.company.name if obj.company else None

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=UserRole.ROLE_CHOICES, default='user', write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'role')
        # Explicitly exclude first_name and last_name fields
        extra_kwargs = {
            'first_name': {'write_only': False, 'read_only': True},
            'last_name': {'write_only': False, 'read_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        role = validated_data.pop('role', 'user')
        
        # Only create user with required fields (username, email)
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            # Explicitly set first_name and last_name to empty strings to avoid any issues
            first_name='',
            last_name=''
        )
        user.set_password(validated_data['password'])
        user.save()
        
        # Create or update profile for user
        UserProfile.objects.get_or_create(user=user)
        
        # Create or update global role for user
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            defaults={'role': role}
        )
        if not created:
            # Update existing role
            user_role.role = role
            user_role.save()
        
        return user

class AdminUserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users in admin panel with company assignment"""
    role = serializers.ChoiceField(choices=UserRole.ROLE_CHOICES, default='user', write_only=True)
    company_id = serializers.PrimaryKeyRelatedField(
        source='company',
        queryset=Company.objects.filter(status='active'),
        required=False,
        allow_null=True,
        write_only=True
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'company_id')
        # Explicitly exclude first_name and last_name fields
        extra_kwargs = {
            'first_name': {'write_only': False, 'read_only': True},
            'last_name': {'write_only': False, 'read_only': True}
        }
    
    def validate(self, attrs):
        role = attrs.get('role', 'user')
        company = attrs.get('company')
        
        # Super admin role must be assigned to Future Objects company
        if role == 'super_admin':
            try:
                futureobjects_company = Company.objects.get(name__iexact='Future Objects', status='active')
                attrs['company'] = futureobjects_company
            except Company.DoesNotExist:
                raise serializers.ValidationError({
                    'company_id': 'Super admin users must be assigned to the Future Objects company. Please create the Future Objects company first.'
                })
        elif not company:
            raise serializers.ValidationError({
                'company_id': 'Company is required for non-super admin users.'
            })
        
        return attrs
    
    def create(self, validated_data):
        role = validated_data.pop('role', 'user')
        company = validated_data.pop('company', None)
        
        # Generate a secure random password
        from django.utils.crypto import get_random_string
        password = get_random_string(16, 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*')
        
        # Only create user with required fields (username, email)
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            # Explicitly set first_name and last_name to empty strings to avoid any issues
            first_name='',
            last_name=''
        )
        user.set_password(password)
        user.save()
        
        # Create or update profile for user with company assignment
        user_profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'company': company}
        )
        if not created:
            # Update existing profile with company
            user_profile.company = company
            user_profile.save()
        
        # Create or update global role for user
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            defaults={'role': role}
        )
        if not created:
            # Update existing role
            user_role.role = role
            user_role.save()
        
        # Store password for email notification
        user._generated_password = password
        
        return user

class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating users in admin panel"""
    role = serializers.ChoiceField(choices=UserRole.ROLE_CHOICES, required=False, write_only=True)
    company_id = serializers.PrimaryKeyRelatedField(
        source='company',
        queryset=Company.objects.filter(status='active'),
        required=False,
        allow_null=True,
        write_only=True
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'is_active', 'company_id')
        # Explicitly exclude first_name and last_name fields
        extra_kwargs = {
            'first_name': {'write_only': False, 'read_only': True},
            'last_name': {'write_only': False, 'read_only': True}
        }
    
    def validate(self, attrs):
        # Check if username is being changed and if it's already taken
        if 'username' in attrs:
            username = attrs['username']
            if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError({
                    'username': 'A user with this username already exists.'
                })
        
        # Check if email is being changed and if it's already taken
        if 'email' in attrs:
            email = attrs['email']
            if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError({
                    'email': 'A user with this email already exists.'
                })
        
        # Check if user is trying to change their own role
        if 'role' in attrs:
            request = self.context.get('request')
            if request and request.user == self.instance:
                raise serializers.ValidationError({
                    'role': 'You cannot change your own role'
                })
        
        # Enforce super admin company assignment rules
        role = attrs.get('role')
        company = attrs.get('company')
        
        # If role is being changed to super_admin, enforce Future Objects company
        if role == 'super_admin':
            try:
                futureobjects_company = Company.objects.get(name__iexact='Future Objects', status='active')
                attrs['company'] = futureobjects_company
            except Company.DoesNotExist:
                raise serializers.ValidationError({
                    'role': 'Super admin users must be assigned to the Future Objects company. Please create the Future Objects company first.'
                })
        # If role is being changed from super_admin to something else, allow company change
        elif role is not None and hasattr(self.instance, 'global_role') and self.instance.global_role.role == 'super_admin':
            # User is being changed from super_admin to another role, allow company assignment
            pass
        # If company is being changed for a super_admin user, enforce Future Objects
        elif company is not None and hasattr(self.instance, 'global_role') and self.instance.global_role.role == 'super_admin':
            try:
                futureobjects_company = Company.objects.get(name__iexact='Future Objects', status='active')
                if company.id != futureobjects_company.id:
                    raise serializers.ValidationError({
                        'company_id': 'Super admin users can only be assigned to the Future Objects company.'
                    })
            except Company.DoesNotExist:
                raise serializers.ValidationError({
                    'company_id': 'Super admin users must be assigned to the Future Objects company. Please create the Future Objects company first.'
                })
        
        return attrs
    
    def update(self, instance, validated_data):
        # Only pop company if it's actually in the validated_data
        company = None
        if 'company' in validated_data:
            company = validated_data.pop('company')
        
        role = validated_data.pop('role', None)
        
        # Update only the required user fields (username, email, is_active)
        # Explicitly exclude first_name and last_name from updates
        allowed_fields = ['username', 'email', 'is_active']
        for attr, value in validated_data.items():
            if attr in allowed_fields:
                setattr(instance, attr, value)
        instance.save()
        
        # Update user role if provided
        if role is not None:
            user_role, created = UserRole.objects.get_or_create(user=instance)
            user_role.role = role
            user_role.save()
        
        # Update user profile company ONLY if company was explicitly provided in the request
        if company is not None:
            user_profile, created = UserProfile.objects.get_or_create(
                user=instance,
                defaults={'company': company}
            )
            if not created:
                # Update existing profile with company
                user_profile.company = company
                user_profile.save()
        
        return instance

class OrganizationMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        source='user',
        queryset=User.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = OrganizationMembership
        fields = ['id', 'user', 'user_id', 'role', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class OrganizationSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'description', 'owner', 'owner_name', 'members_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'owner_name', 'members_count', 'created_at', 'updated_at']
    
    def get_owner_name(self, obj):
        return obj.owner.username if obj.owner else None
    
    def get_members_count(self, obj):
        return obj.members.count()

class OrganizationDetailSerializer(OrganizationSerializer):
    members = OrganizationMembershipSerializer(source='organizationmembership_set', many=True, read_only=True)
    
    class Meta(OrganizationSerializer.Meta):
        fields = OrganizationSerializer.Meta.fields + ['members']

class ProjectSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 
            'organization', 'organization_name',
            'owner', 'owner_name', 
            'is_public',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'owner_name', 'organization_name', 'created_at', 'updated_at']
    
    def get_owner_name(self, obj):
        return obj.owner.username if obj.owner else None
    
    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None

class ProjectDetailSerializer(ProjectSerializer):
    authorized_users = UserSerializer(many=True, read_only=True)
    
    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['authorized_users'] 

class PlatformSerializer(serializers.ModelSerializer):
    """Serializer for Platform model"""
    available_services = serializers.SerializerMethodField()
    
    class Meta:
        model = Platform
        fields = [
            'id', 'name', 'display_name', 'is_enabled', 'description', 
            'icon_name', 'color', 'available_services', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_available_services(self, obj):
        """Get available services for this platform"""
        platform_services = obj.get_available_services()
        # Extract the Service objects from PlatformService objects
        services = [ps.service for ps in platform_services]
        return ServiceSerializer(services, many=True).data

class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for Service model"""
    
    class Meta:
        model = Service
        fields = [
            'id', 'name', 'display_name', 'description', 
            'icon_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class PlatformServiceSerializer(serializers.ModelSerializer):
    """Serializer for PlatformService model"""
    platform = PlatformSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)
    is_available = serializers.ReadOnlyField()
    
    class Meta:
        model = PlatformService
        fields = [
            'id', 'platform', 'service', 'is_enabled', 'is_available',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_available', 'created_at', 'updated_at']

class PlatformServiceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating PlatformService instances"""
    platform_id = serializers.PrimaryKeyRelatedField(
        source='platform',
        queryset=Platform.objects.all(),
        write_only=True
    )
    service_id = serializers.PrimaryKeyRelatedField(
        source='service',
        queryset=Service.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = PlatformService
        fields = [
            'platform_id', 'service_id', 'is_enabled', 'description'
        ]
    
    def validate(self, data):
        platform = data.get('platform')
        service = data.get('service')
        
        if PlatformService.objects.filter(platform=platform, service=service).exists():
            raise serializers.ValidationError("This platform-service combination already exists.")
        
        return data

class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'status', 'status_display', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 

class UnifiedUserRecordSerializer(serializers.ModelSerializer):
    """Serializer for UnifiedUserRecord model"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UnifiedUserRecord
        fields = [
            'id', 'name', 'email', 'company', 'company_name', 
            'role', 'role_display', 'status', 'status_display',
            'username', 'created_date', 'updated_date'
        ]
        read_only_fields = ['id', 'created_date', 'updated_date', 'company_name', 'role_display', 'status_display', 'username']
    
    def to_representation(self, instance):
        """Custom representation to include additional computed fields"""
        data = super().to_representation(instance)
        data['display_name'] = instance.display_name
        return data 