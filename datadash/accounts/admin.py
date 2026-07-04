from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, LoginHistory


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_staff', 'email_verified', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'email_verified', 'theme')
    search_fields = ('email', 'username')
    ordering = ('-created_at',)
    fieldsets = UserAdmin.fieldsets + (
        ('DataDash Profile', {'fields': ('avatar', 'bio', 'theme', 'default_view', 'email_verified')}),
    )


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'timestamp', 'success')
    list_filter = ('success',)
    search_fields = ('user__email',)
    ordering = ('-timestamp',)
