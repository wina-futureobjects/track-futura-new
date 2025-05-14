from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, Project, Organization, OrganizationMembership, UserRole

class UserRoleSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = UserRole
        fields = ['role', 'role_display']
        read_only_fields = ['role_display']

class UserSerializer(serializers.ModelSerializer):
    global_role = UserRoleSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'global_role']
        read_only_fields = ['id', 'global_role']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'avatar', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=UserRole.ROLE_CHOICES, default='user', write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name', 'role')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        role = validated_data.pop('role', 'user')
        
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        
        # Create profile for user
        UserProfile.objects.create(user=user)
        
        # Create global role for user
        UserRole.objects.create(user=user, role=role)
        
        return user

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