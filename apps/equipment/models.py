from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.branches.models import Branch

from .managers import EquipmentManager


class EquipmentStatus(models.TextChoices):
    ACTIVE = "ACTIVE", _("Operativo")
    INACTIVE = "INACTIVE", _("Fuera de servicio")
    IN_MAINTENANCE = "IN_MAINTENANCE", _("En mantenimiento")
    IN_REPAIR = "IN_REPAIR", _("En reparación")


class Equipment(models.Model):
    name = models.CharField(_("Nombre"), max_length=150)
    asset_tag = models.CharField(
        _("Código de inventario"), max_length=50, unique=True, db_index=True
    )
    brand = models.CharField(_("Marca"), max_length=80)
    model = models.CharField(_("Modelo"), max_length=80)
    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="equipment",
        verbose_name=_("Sede"),
    )
    location = models.CharField(_("Ubicación"), max_length=120, blank=True)
    purchase_date = models.DateField(_("Fecha de compra"), null=True, blank=True)
    status = models.CharField(
        _("Estado"),
        max_length=20,
        choices=EquipmentStatus.choices,
        default=EquipmentStatus.ACTIVE,
        db_index=True,
    )
    qr_code = models.FileField(
        _("Código QR"), upload_to="equipment/qr/", blank=True
    )
    created_at = models.DateTimeField(_("Creado"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Actualizado"), auto_now=True)

    objects = EquipmentManager()

    class Meta:
        verbose_name = _("Equipo biomédico")
        verbose_name_plural = _("Equipos biomédicos")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["asset_tag"], name="equipment_asset_tag_idx"),
            models.Index(fields=["branch"], name="equipment_branch_idx"),
            models.Index(fields=["status"], name="equipment_status_idx"),
            models.Index(fields=["brand"], name="equipment_brand_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.asset_tag})"
