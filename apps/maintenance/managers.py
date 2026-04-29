from django.db import models


class MaintenanceRecordQuerySet(models.QuerySet):
    def for_equipment(self, equipment_id: int) -> "MaintenanceRecordQuerySet":
        return self.filter(equipment_id=equipment_id)

    def for_branch(self, branch_id: int) -> "MaintenanceRecordQuerySet":
        return self.filter(equipment__branch_id=branch_id)

    def of_kind(self, kind: str) -> "MaintenanceRecordQuerySet":
        return self.filter(kind=kind)

    def preventive(self) -> "MaintenanceRecordQuerySet":
        return self.of_kind("PREVENTIVE")

    def corrective(self) -> "MaintenanceRecordQuerySet":
        return self.of_kind("CORRECTIVE")

    def repairs(self) -> "MaintenanceRecordQuerySet":
        return self.of_kind("REPAIR")

    def in_range(self, start, end) -> "MaintenanceRecordQuerySet":
        return self.filter(date__gte=start, date__lte=end)


class MaintenanceRecordManager(models.Manager.from_queryset(MaintenanceRecordQuerySet)):
    def get_queryset(self) -> MaintenanceRecordQuerySet:
        return MaintenanceRecordQuerySet(self.model, using=self._db).select_related(
            "equipment", "equipment__branch"
        )
