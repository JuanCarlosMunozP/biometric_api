from django_filters import rest_framework as filters

from apps.equipment.models import Equipment


class EquipmentFilter(filters.FilterSet):
    branch = filters.NumberFilter(field_name="branch_id")
    status = filters.CharFilter(field_name="status", lookup_expr="iexact")
    brand = filters.CharFilter(field_name="brand", lookup_expr="icontains")
    purchase_date_after = filters.DateFilter(
        field_name="purchase_date", lookup_expr="gte"
    )
    purchase_date_before = filters.DateFilter(
        field_name="purchase_date", lookup_expr="lte"
    )

    class Meta:
        model = Equipment
        fields = (
            "branch",
            "status",
            "brand",
            "purchase_date_after",
            "purchase_date_before",
        )
