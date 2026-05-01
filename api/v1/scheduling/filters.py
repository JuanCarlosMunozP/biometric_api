from django_filters import rest_framework as filters

from apps.scheduling.models import MaintenanceSchedule


class MaintenanceScheduleFilter(filters.FilterSet):
    equipment = filters.NumberFilter(field_name="equipment_id")
    branch = filters.NumberFilter(field_name="equipment__branch_id")
    kind = filters.CharFilter(field_name="kind", lookup_expr="iexact")
    is_completed = filters.BooleanFilter(field_name="is_completed")
    scheduled_date_after = filters.DateFilter(field_name="scheduled_date", lookup_expr="gte")
    scheduled_date_before = filters.DateFilter(field_name="scheduled_date", lookup_expr="lte")

    class Meta:
        model = MaintenanceSchedule
        fields = (
            "equipment",
            "branch",
            "kind",
            "is_completed",
            "scheduled_date_after",
            "scheduled_date_before",
        )
