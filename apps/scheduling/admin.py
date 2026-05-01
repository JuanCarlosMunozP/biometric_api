from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import MaintenanceSchedule


@admin.register(MaintenanceSchedule)
class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "equipment",
        "kind",
        "scheduled_date",
        "is_completed",
        "notified_at",
        "created_at",
    )
    list_filter = ("kind", "is_completed", "scheduled_date", "equipment__branch")
    search_fields = ("notes", "equipment__asset_tag", "equipment__name")
    ordering = ("scheduled_date",)
    autocomplete_fields = ("equipment",)
    readonly_fields = ("notified_at", "created_at", "updated_at")
    fieldsets = (
        (
            _("Información general"),
            {"fields": ("equipment", "kind", "scheduled_date", "notes", "is_completed")},
        ),
        (
            _("Notificación"),
            {"fields": ("notified_at",)},
        ),
        (
            _("Auditoría"),
            {"fields": ("created_at", "updated_at")},
        ),
    )
