from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import MaintenanceRecord


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ("equipment", "kind", "date", "technician", "cost", "created_at")
    list_filter = ("kind", "date", "equipment__branch")
    search_fields = ("description", "technician", "equipment__asset_tag", "equipment__name")
    ordering = ("-date", "-created_at")
    autocomplete_fields = ("equipment",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            _("Información general"),
            {"fields": ("equipment", "kind", "date", "description", "technician", "cost")},
        ),
        (
            _("Documentación"),
            {"fields": ("pdf_file",)},
        ),
        (
            _("Auditoría"),
            {"fields": ("created_at", "updated_at")},
        ),
    )
