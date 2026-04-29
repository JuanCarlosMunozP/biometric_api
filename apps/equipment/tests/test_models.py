import pytest

from apps.equipment.models import Equipment, EquipmentStatus

from .factories import EquipmentFactory


@pytest.mark.django_db
class TestEquipmentModel:
    def test_str(self, equipment):
        assert str(equipment) == f"{equipment.name} ({equipment.asset_tag})"

    def test_default_status_is_active(self, branch):
        eq = Equipment(name="x", asset_tag="EQ-X", brand="b", model="m", branch=branch)
        assert eq.status == EquipmentStatus.ACTIVE


@pytest.mark.django_db
class TestEquipmentManager:
    def test_active_returns_only_active(self):
        EquipmentFactory(status=EquipmentStatus.ACTIVE)
        EquipmentFactory(status=EquipmentStatus.INACTIVE)
        EquipmentFactory(status=EquipmentStatus.IN_REPAIR)
        assert Equipment.objects.active().count() == 1

    def test_in_repair_returns_maintenance_and_repair(self):
        EquipmentFactory(status=EquipmentStatus.ACTIVE)
        EquipmentFactory(status=EquipmentStatus.IN_MAINTENANCE)
        EquipmentFactory(status=EquipmentStatus.IN_REPAIR)
        assert Equipment.objects.in_repair().count() == 2

    def test_for_branch_filters_by_branch_id(self, branch):
        EquipmentFactory.create_batch(2, branch=branch)
        EquipmentFactory()
        assert Equipment.objects.for_branch(branch.id).count() == 2

    def test_select_related_branch_avoids_n_plus_1(
        self, django_assert_num_queries
    ):
        EquipmentFactory.create_batch(3)
        with django_assert_num_queries(1):
            for eq in Equipment.objects.all():
                _ = eq.branch.name
