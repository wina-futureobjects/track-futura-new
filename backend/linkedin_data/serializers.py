from rest_framework import serializers
from .models import LinkedInPost, Folder

class LinkedInPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkedInPost
        fields = '__all__'

class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = '__all__' 