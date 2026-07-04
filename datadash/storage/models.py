import uuid
import os
from django.db import models
from django.conf import settings
from django.utils import timezone


def upload_to(instance, filename):
    ext = filename.split('.')[-1]
    return f'uploads/{instance.owner.id}/{uuid.uuid4()}.{ext}'


class Folder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='folders')
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    color = models.CharField(max_length=20, default='#6366f1')
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ('owner', 'name', 'parent')

    def __str__(self):
        return self.name

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
        for f in self.files.all():
            f.soft_delete()
        for child in self.children.all():
            child.soft_delete()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()


class UserFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='files')
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True, blank=True, related_name='files')
    name = models.CharField(max_length=255)
    original_name = models.CharField(max_length=255)
    file = models.FileField(upload_to=upload_to)
    size = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    def get_icon(self):
        icons = {
            'image': 'photo',
            'video': 'video',
            'audio': 'music',
            'text': 'file-text',
            'application/pdf': 'file-pdf',
            'application/zip': 'file-zip',
            'application/x-zip-compressed': 'file-zip',
            'application/msword': 'file-word',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'file-word',
            'application/vnd.ms-excel': 'file-spreadsheet',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'file-spreadsheet',
        }
        for key, icon in icons.items():
            if self.mime_type.startswith(key) or self.mime_type == key:
                return icon
        return 'file'

    def is_image(self):
        return self.mime_type.startswith('image/')

    def get_size_display(self):
        size = self.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


class SharedFile(models.Model):
    PERMISSION_CHOICES = [('view', 'View'), ('edit', 'Edit')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(UserFile, on_delete=models.CASCADE, related_name='shares', null=True, blank=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='shares', null=True, blank=True)
    shared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shared_by_me')
    shared_with = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shared_with_me', null=True, blank=True)
    shared_with_email = models.EmailField(blank=True)
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default='view')
    share_link = models.UUIDField(default=uuid.uuid4, unique=True)
    is_public = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        item = self.file or self.folder
        return f"{item} shared by {self.shared_by}"

    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def get_item_name(self):
        if self.file:
            return self.file.name
        if self.folder:
            return self.folder.name
        return 'Unknown'


class UserStorageUsage(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='storage')
    used_bytes = models.BigIntegerField(default=0)
    max_bytes = models.BigIntegerField(default=3221225472)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}: {self.used_bytes}/{self.max_bytes}"

    def percentage(self):
        return min(round((self.used_bytes / self.max_bytes) * 100, 1), 100)

    def is_near_limit(self):
        return self.percentage() >= 90

    def is_at_limit(self):
        return self.used_bytes >= self.max_bytes

    def remaining_bytes(self):
        return max(self.max_bytes - self.used_bytes, 0)
