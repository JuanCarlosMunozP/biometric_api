import pytest

from apps.equipment.models import Equipment

from .factories import EquipmentFactory


@pytest.mark.django_db
class TestAutoGenerateQrSignal:
    def test_post_save_generates_qr_on_create(self, branch):
        eq = Equipment.objects.create(
            name="Nuevo",
            asset_tag="EQ-NEW-1",
            brand="b",
            model="m",
            branch=branch,
        )
        eq.refresh_from_db()
        assert eq.qr_code
        assert eq.qr_code.storage.exists(eq.qr_code.name)

    def test_post_save_does_not_regenerate_on_update(self, equipment):
        original_name = equipment.qr_code.name
        equipment.location = "UCI"
        equipment.save()
        equipment.refresh_from_db()
        assert equipment.qr_code.name == original_name


@pytest.mark.django_db
class TestRemoveQrFileSignal:
    def test_pre_delete_removes_file_from_storage(self, equipment):
        storage = equipment.qr_code.storage
        path = equipment.qr_code.name
        assert storage.exists(path)
        equipment.delete()
        assert not storage.exists(path)
