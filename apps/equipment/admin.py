from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Equipment


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("name", "asset_tag", "brand", "model", "branch", "status", "created_at")
    list_filter = ("status", "branch", "brand")
    search_fields = ("name", "asset_tag", "model", "brand")
    ordering = ("name",)
    readonly_fields = ("qr_code", "created_at", "updated_at")
    autocomplete_fields = ("branch",)
    fieldsets = (
        (_("Identificación"), {"fields": ("name", "asset_tag", "brand", "model")}),
        (_("Ubicación y estado"), {"fields": ("branch", "location", "status", "purchase_date")}),
        (_("Código QR"), {"fields": ("qr_code",)}),
        (_("Auditoría"), {"fields": ("created_at", "updated_at")}),
    )
