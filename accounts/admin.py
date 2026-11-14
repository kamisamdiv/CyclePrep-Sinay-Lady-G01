from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'cycle_type', 'contact_number', 'created_at')
    list_filter = ('role', 'cycle_type')
    search_fields = ('user__username', 'user__email')
