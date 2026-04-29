import factory
from factory.django import DjangoModelFactory

from apps.branches.tests.factories import BranchFactory
from apps.equipment.models import Equipment, EquipmentStatus


class EquipmentFactory(DjangoModelFactory):
    class Meta:
        model = Equipment

    name = factory.Sequence(lambda n: f"Equipo {n}")
    asset_tag = factory.Sequence(lambda n: f"EQ-{n:04d}")
    brand = factory.Iterator(["Philips", "GE", "Mindray", "Siemens"])
    model = factory.Sequence(lambda n: f"M-{n}")
    branch = factory.SubFactory(BranchFactory)
    location = ""
    purchase_date = None
    status = EquipmentStatus.ACTIVE
