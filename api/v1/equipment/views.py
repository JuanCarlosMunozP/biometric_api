from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.equipment.models import Equipment
from apps.equipment.services import generate_qr_for_equipment

from .filters import EquipmentFilter
from .serializers import EquipmentSerializer


class EquipmentViewSet(viewsets.ModelViewSet):
    """CRUD de equipos biomédicos + búsqueda por asset_tag y regeneración de QR."""

    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = EquipmentFilter
    search_fields = ("name", "asset_tag", "model")
    ordering_fields = ("name", "purchase_date", "created_at")
    ordering = ("name",)

    @action(
        detail=False,
        methods=["get"],
        url_path=r"by-asset-tag/(?P<tag>[^/.]+)",
        url_name="by-asset-tag",
    )
    def by_asset_tag(self, request, tag: str = ""):
        equipment = get_object_or_404(
            Equipment, asset_tag__iexact=tag.strip()
        )
        serializer = self.get_serializer(equipment)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="regenerate-qr")
    def regenerate_qr(self, request, pk: int = None):
        equipment = self.get_object()
        if equipment.qr_code:
            equipment.qr_code.delete(save=False)
        generate_qr_for_equipment(equipment)
        equipment.refresh_from_db()
        serializer = self.get_serializer(equipment)
        return Response(serializer.data, status=status.HTTP_200_OK)
