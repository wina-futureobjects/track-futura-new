from django.contrib import admin
from .models import FacebookPost, Folder

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(FacebookPost)
class FacebookPostAdmin(admin.ModelAdmin):
    list_display = ('user_posted', 'post_id', 'content_type', 'likes', 'folder', 'date_posted')
    list_filter = ('content_type', 'is_verified', 'is_paid_partnership', 'folder')
    search_fields = ('user_posted', 'description', 'hashtags')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date_posted'
    ordering = ('-date_posted',)
    raw_id_fields = ('folder',)
    list_select_related = ('folder',) 