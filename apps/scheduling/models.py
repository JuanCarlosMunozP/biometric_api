from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.equipment.models import Equipment

from .managers import MaintenanceScheduleManager


class ScheduledMaintenanceKind(models.TextChoices):
    PREVENTIVE = "PREVENTIVE", _("Mantenimiento preventivo")
    REPAIR = "REPAIR", _("Reparación programada")


class MaintenanceSchedule(models.Model):
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.PROTECT,
        related_name="schedules",
        verbose_name=_("Equipo"),
    )
    kind = models.CharField(
        _("Tipo"),
        max_length=20,
        choices=ScheduledMaintenanceKind.choices,
        db_index=True,
    )
    scheduled_date = models.DateField(_("Fecha programada"), db_index=True)
    notes = models.TextField(_("Notas"), blank=True)
    notified_at = models.DateTimeField(_("Notificado el"), null=True, blank=True)
    is_completed = models.BooleanField(_("Completado"), default=False, db_index=True)
    created_at = models.DateTimeField(_("Creado"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Actualizado"), auto_now=True)

    objects = MaintenanceScheduleManager()

    class Meta:
        verbose_name = _("Agendamiento de mantenimiento")
        verbose_name_plural = _("Agendamientos de mantenimiento")
        ordering = ["scheduled_date"]
        indexes = [
            models.Index(fields=["equipment", "scheduled_date"], name="sched_eq_date_idx"),
            models.Index(fields=["scheduled_date", "is_completed"], name="sched_date_comp_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.get_kind_display()} - {self.equipment.asset_tag} - {self.scheduled_date}"
