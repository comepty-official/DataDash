from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    theme = models.CharField(
        max_length=10,
        choices=[('dark', 'Dark'), ('light', 'Light'), ('system', 'System')],
        default='dark'
    )
    email_verified = models.BooleanField(default=False)
    default_view = models.CharField(
        max_length=10,
        choices=[('grid', 'Grid'), ('list', 'List')],
        default='grid'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    def get_storage_used(self):
        from storage.models import UserFile
        from django.db.models import Sum
        result = UserFile.objects.filter(owner=self, is_deleted=False).aggregate(
            total=Sum('size')
        )
        return result['total'] or 0

    def get_storage_percentage(self):
        from django.conf import settings
        used = self.get_storage_used()
        return min(round((used / settings.MAX_STORAGE_BYTES) * 100, 1), 100)

    def get_file_count(self):
        from storage.models import UserFile
        return UserFile.objects.filter(owner=self, is_deleted=False).count()

    def get_photo_count(self):
        from storage.models import UserFile
        image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml']
        return UserFile.objects.filter(
            owner=self, is_deleted=False, mime_type__in=image_types
        ).count()


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Login histories'

    def __str__(self):
        return f"{self.user.email} — {self.timestamp}"
