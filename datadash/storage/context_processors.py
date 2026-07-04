from django.conf import settings


def storage_context(request):
    if request.user.is_authenticated:
        from .models import UserStorageUsage
        usage, _ = UserStorageUsage.objects.get_or_create(
            user=request.user,
            defaults={'max_bytes': settings.MAX_STORAGE_BYTES}
        )
        return {
            'storage_usage': usage,
            'storage_percent': usage.percentage(),
        }
    return {}
