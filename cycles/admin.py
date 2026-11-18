from django.contrib import admin

from .models import CycleLog, Symptom


@admin.register(CycleLog)
class CycleLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'created_at')
    list_filter = ('start_date',)
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('symptoms',)


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ('name',)
