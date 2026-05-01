from django.db import models


class MaintenanceScheduleQuerySet(models.QuerySet):
    def for_equipment(self, equipment_id: int) -> "MaintenanceScheduleQuerySet":
        return self.filter(equipment_id=equipment_id)

    def for_branch(self, branch_id: int) -> "MaintenanceScheduleQuerySet":
        return self.filter(equipment__branch_id=branch_id)

    def pending(self) -> "MaintenanceScheduleQuerySet":
        return self.filter(is_completed=False)

    def completed(self) -> "MaintenanceScheduleQuerySet":
        return self.filter(is_completed=True)

    def in_range(self, start, end) -> "MaintenanceScheduleQuerySet":
        return self.filter(scheduled_date__gte=start, scheduled_date__lte=end)


class MaintenanceScheduleManager(
    models.Manager.from_queryset(MaintenanceScheduleQuerySet)
):
    def get_queryset(self) -> MaintenanceScheduleQuerySet:
        return MaintenanceScheduleQuerySet(self.model, using=self._db).select_related(
            "equipment", "equipment__branch"
        )
