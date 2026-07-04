from django.contrib import admin
from .models import UserFile, Folder, SharedFile, UserStorageUsage


@admin.register(UserFile)
class UserFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'size', 'mime_type', 'is_deleted', 'created_at')
    list_filter = ('is_deleted', 'is_favorite')
    search_fields = ('name', 'owner__email')
    ordering = ('-created_at',)


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'parent', 'is_deleted', 'created_at')
    list_filter = ('is_deleted',)
    search_fields = ('name', 'owner__email')


@admin.register(SharedFile)
class SharedFileAdmin(admin.ModelAdmin):
    list_display = ('get_item_name', 'shared_by', 'shared_with_email', 'permission', 'created_at')
    search_fields = ('shared_by__email', 'shared_with_email')
    ordering = ('-created_at',)


@admin.register(UserStorageUsage)
class UserStorageUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'used_bytes', 'max_bytes', 'updated_at')
    search_fields = ('user__email',)
