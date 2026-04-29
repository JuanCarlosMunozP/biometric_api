from django_filters import rest_framework as filters

from apps.maintenance.models import MaintenanceRecord


class MaintenanceRecordFilter(filters.FilterSet):
    equipment = filters.NumberFilter(field_name="equipment_id")
    branch = filters.NumberFilter(field_name="equipment__branch_id")
    kind = filters.CharFilter(field_name="kind", lookup_expr="iexact")
    date_after = filters.DateFilter(field_name="date", lookup_expr="gte")
    date_before = filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = MaintenanceRecord
        fields = ("equipment", "branch", "kind", "date_after", "date_before")
