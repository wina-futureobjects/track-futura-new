from rest_framework import serializers
from .models import TikTokPost, Folder

class TikTokPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = TikTokPost
        fields = '__all__'

class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = '__all__' 