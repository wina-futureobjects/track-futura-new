from django.contrib import admin
from .models import LinkedInPost, Folder

class LinkedInPostAdmin(admin.ModelAdmin):
    list_display = ('user_posted', 'date_posted', 'likes', 'num_comments', 'content_type')
    list_filter = ('content_type', 'is_verified', 'is_paid_partnership')
    search_fields = ('user_posted', 'description', 'hashtags')
    date_hierarchy = 'date_posted'
    raw_id_fields = ('folder',)

class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')

admin.site.register(LinkedInPost, LinkedInPostAdmin)
admin.site.register(Folder, FolderAdmin) 