from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.equipment.models import EquipmentStatus
from apps.scheduling.models import MaintenanceSchedule


class MaintenanceScheduleSerializer(serializers.ModelSerializer):
    equipment_asset_tag = serializers.CharField(source="equipment.asset_tag", read_only=True)
    branch_name = serializers.CharField(source="equipment.branch.name", read_only=True)

    class Meta:
        model = MaintenanceSchedule
        fields = (
            "id",
            "equipment",
            "equipment_asset_tag",
            "branch_name",
            "kind",
            "scheduled_date",
            "notes",
            "notified_at",
            "is_completed",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "equipment_asset_tag",
            "branch_name",
            "notified_at",
            "created_at",
            "updated_at",
        )

    def validate_equipment(self, value):
        if value.status == EquipmentStatus.INACTIVE:
            raise serializers.ValidationError(
                _("El equipo no está disponible para programación.")
            )
        return value

    def validate_scheduled_date(self, value):
        if self.instance is None and value < timezone.localdate():
            raise serializers.ValidationError(
                _("La fecha programada no puede ser pasada.")
            )
        return value

    def validate_notes(self, value):
        return value.strip() if value else value
