from rest_framework import serializers
from .models import FacebookPost, Folder

class FolderSerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Folder
        fields = ['id', 'name', 'description', 'project', 'created_at', 'updated_at', 'post_count']
    
    def get_post_count(self, obj):
        return obj.posts.count()

class FacebookPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacebookPost
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at') 