from rest_framework import serializers
from .models import TikTokPost, Folder

class TikTokPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = TikTokPost
        fields = '__all__'

class FolderSerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Folder
        fields = ['id', 'name', 'description', 'project', 'created_at', 'updated_at', 'post_count']
    
    def get_post_count(self, obj):
        return obj.posts.count() 