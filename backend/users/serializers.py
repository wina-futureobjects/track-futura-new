from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, Project, Organization, OrganizationMembership, UserRole, Platform, Service, PlatformService, Company

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
        fields = ['id', 'username', 'email', 'global_role', 'is_active', 'company_name', 'company_id']
        read_only_fields = ['id', 'global_role', 'company_name', 'company_id']
    
    def get_company_name(self, obj):
        if hasattr(obj, 'profile') and obj.profile.company:
            return obj.profile.company.name
        return None
    
    def get_company_id(self, obj):
        if hasattr(obj, 'profile') and obj.profile.company:
            return obj.profile.company.id
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

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        role = validated_data.pop('role', 'user')
        
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        
        # Create profile for user
        UserProfile.objects.create(user=user)
        
        # Create global role for user
        UserRole.objects.create(user=user, role=role)
        
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
    
    def validate(self, attrs):
        role = attrs.get('role', 'user')
        company = attrs.get('company')
        
        # Super admin role must be assigned to futureobjects company
        if role == 'super_admin':
            try:
                futureobjects_company = Company.objects.get(name__iexact='futureobjects', status='active')
                attrs['company'] = futureobjects_company
            except Company.DoesNotExist:
                raise serializers.ValidationError({
                    'company_id': 'Super admin users must be assigned to the FutureObjects company. Please create the FutureObjects company first.'
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
        
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(password)
        user.save()
        
        # Create profile for user with company assignment
        UserProfile.objects.create(user=user, company=company)
        
        # Create global role for user
        UserRole.objects.create(user=user, role=role)
        
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
        
        return attrs
    
    def update(self, instance, validated_data):
        company = validated_data.pop('company', None)
        role = validated_data.pop('role', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update user role if provided
        if role is not None:
            user_role, created = UserRole.objects.get_or_create(user=instance)
            user_role.role = role
            user_role.save()
        
        # Update user profile company
        if hasattr(instance, 'profile'):
            instance.profile.company = company
            instance.profile.save()
        else:
            UserProfile.objects.create(user=instance, company=company)
        
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
    created_by_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'email', 'status', 'status_display', 'phone', 'address', 'website',
            'industry', 'size', 'description', 'notes', 'contact_person', 'contact_email',
            'contact_phone', 'created_at', 'updated_at', 'created_by', 'created_by_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'created_by_name']
    
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None 