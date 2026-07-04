import mimetypes
from django.conf import settings
from .models import UserStorageUsage


def get_mime_type(file):
    mime_type, _ = mimetypes.guess_type(file.name)
    return mime_type or 'application/octet-stream'


def update_storage_usage(user):
    from .models import UserFile
    from django.db.models import Sum
    result = UserFile.objects.filter(owner=user, is_deleted=False).aggregate(
        total=Sum('size')
    )
    total = result['total'] or 0
    usage, _ = UserStorageUsage.objects.get_or_create(
        user=user,
        defaults={'max_bytes': settings.MAX_STORAGE_BYTES}
    )
    usage.used_bytes = total
    usage.save()
    return usage


def check_storage_limit(user, file_size):
    usage, _ = UserStorageUsage.objects.get_or_create(
        user=user,
        defaults={'max_bytes': settings.MAX_STORAGE_BYTES}
    )
    return (usage.used_bytes + file_size) <= usage.max_bytes


def format_bytes(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"
