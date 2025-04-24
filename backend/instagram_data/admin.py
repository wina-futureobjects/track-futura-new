from django.contrib import admin
from .models import InstagramPost, Folder

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'get_post_count', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    def get_post_count(self, obj):
        return obj.posts.count()
    get_post_count.short_description = 'Post Count'

@admin.register(InstagramPost)
class InstagramPostAdmin(admin.ModelAdmin):
    list_display = ('user_posted', 'post_id', 'content_type', 'likes', 'folder', 'date_posted')
    list_filter = ('content_type', 'is_verified', 'is_paid_partnership', 'folder')
    search_fields = ('user_posted', 'description', 'hashtags')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date_posted'
    ordering = ('-date_posted',)
    raw_id_fields = ('folder',)
    list_select_related = ('folder',)
