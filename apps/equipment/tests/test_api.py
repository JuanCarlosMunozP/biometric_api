from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.branches.tests.factories import BranchFactory
from apps.equipment.models import Equipment, EquipmentStatus

from .factories import EquipmentFactory


LIST_URL = reverse("v1:equipment:equipment-list")


def detail_url(pk):
    return reverse("v1:equipment:equipment-detail", args=[pk])


def by_tag_url(tag):
    return reverse("v1:equipment:equipment-by-asset-tag", args=[tag])


def regenerate_url(pk):
    return reverse("v1:equipment:equipment-regenerate-qr", args=[pk])


@pytest.mark.django_db
class TestEquipmentAuth:
    def test_list_requires_auth(self, api_client):
        assert api_client.get(LIST_URL).status_code == 401

    def test_create_requires_auth(self, api_client, branch):
        payload = {"name": "x", "asset_tag": "EQ-1", "brand": "b", "model": "m", "branch": branch.id}
        assert api_client.post(LIST_URL, payload, format="json").status_code == 401


@pytest.mark.django_db
class TestEquipmentCreate:
    def _payload(self, branch):
        return {
            "name": "Monitor de signos vitales",
            "asset_tag": "EQ-0001",
            "brand": "Philips",
            "model": "MX450",
            "branch": branch.id,
            "location": "UCI - cama 3",
            "purchase_date": "2024-08-15",
            "status": EquipmentStatus.ACTIVE,
        }

    def test_create_201_and_qr_url_present(self, auth_client, branch):
        response = auth_client.post(LIST_URL, self._payload(branch), format="json")
        assert response.status_code == 201
        body = response.json()
        assert body["qr_code_url"]
        assert body["qr_code_url"].startswith("http")
        assert body["asset_tag"] == "EQ-0001"
        assert body["branch_name"] == branch.name

    def test_asset_tag_normalized_to_uppercase(self, auth_client, branch):
        payload = self._payload(branch)
        payload["asset_tag"] = "  eq-abc  "
        response = auth_client.post(LIST_URL, payload, format="json")
        assert response.status_code == 201
        assert response.json()["asset_tag"] == "EQ-ABC"

    def test_duplicate_asset_tag_case_insensitive(self, auth_client, branch):
        EquipmentFactory(asset_tag="EQ-0001", branch=branch)
        payload = self._payload(branch)
        payload["asset_tag"] = "eq-0001"
        response = auth_client.post(LIST_URL, payload, format="json")
        assert response.status_code == 400
        assert "código de inventario" in str(response.json()).lower()

    def test_future_purchase_date_returns_400(self, auth_client, branch):
        payload = self._payload(branch)
        future = (timezone.localdate() + timedelta(days=10)).isoformat()
        payload["purchase_date"] = future
        response = auth_client.post(LIST_URL, payload, format="json")
        assert response.status_code == 400
        assert "fecha de compra" in str(response.json()).lower()

    def test_inactive_branch_returns_400(self, auth_client):
        inactive = BranchFactory(is_active=False)
        payload = self._payload(inactive)
        response = auth_client.post(LIST_URL, payload, format="json")
        assert response.status_code == 400
        assert "no está activa" in str(response.json()).lower()

    def test_missing_required_fields(self, auth_client):
        response = auth_client.post(LIST_URL, {}, format="json")
        assert response.status_code == 400
        for field in ("name", "asset_tag", "brand", "model", "branch"):
            assert field in response.json()


@pytest.mark.django_db
class TestEquipmentList:
    def test_list_paginated(self, auth_client):
        EquipmentFactory.create_batch(3)
        response = auth_client.get(LIST_URL)
        assert response.status_code == 200
        assert "results" in response.json()
        assert response.json()["count"] == 3

    def test_filter_by_branch(self, auth_client):
        target = BranchFactory()
        EquipmentFactory.create_batch(2, branch=target)
        EquipmentFactory()
        response = auth_client.get(LIST_URL, {"branch": target.id})
        assert response.json()["count"] == 2

    def test_filter_by_status(self, auth_client):
        EquipmentFactory(status=EquipmentStatus.ACTIVE)
        EquipmentFactory(status=EquipmentStatus.IN_MAINTENANCE)
        response = auth_client.get(LIST_URL, {"status": "ACTIVE"})
        assert response.json()["count"] == 1

    def test_filter_by_brand_icontains(self, auth_client):
        EquipmentFactory(brand="Philips Medical")
        EquipmentFactory(brand="GE")
        response = auth_client.get(LIST_URL, {"brand": "philips"})
        assert response.json()["count"] == 1

    def test_filter_by_purchase_date_range(self, auth_client):
        EquipmentFactory(purchase_date="2024-06-01")
        EquipmentFactory(purchase_date="2024-12-31")
        EquipmentFactory(purchase_date="2023-01-01")
        response = auth_client.get(
            LIST_URL,
            {"purchase_date_after": "2024-01-01", "purchase_date_before": "2024-12-31"},
        )
        assert response.json()["count"] == 2

    def test_search_by_asset_tag(self, auth_client):
        EquipmentFactory(asset_tag="EQ-ABC")
        EquipmentFactory(asset_tag="EQ-ZZZ")
        response = auth_client.get(LIST_URL, {"search": "ABC"})
        tags = [e["asset_tag"] for e in response.json()["results"]]
        assert "EQ-ABC" in tags

    def test_ordering_by_name(self, auth_client):
        EquipmentFactory(name="Zeta")
        EquipmentFactory(name="Alfa")
        response = auth_client.get(LIST_URL, {"ordering": "name"})
        names = [e["name"] for e in response.json()["results"]]
        assert names == sorted(names)


@pytest.mark.django_db
class TestEquipmentRetrieve:
    def test_retrieve_includes_qr_code_url(self, auth_client, equipment):
        response = auth_client.get(detail_url(equipment.id))
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == equipment.id
        assert body["qr_code_url"]

    def test_retrieve_missing_returns_404(self, auth_client):
        assert auth_client.get(detail_url(99999)).status_code == 404


@pytest.mark.django_db
class TestEquipmentByAssetTag:
    def test_resolve_by_tag_case_insensitive(self, auth_client, equipment):
        response = auth_client.get(by_tag_url(equipment.asset_tag.lower()))
        assert response.status_code == 200
        assert response.json()["id"] == equipment.id

    def test_unknown_tag_returns_404(self, auth_client):
        assert auth_client.get(by_tag_url("DOES-NOT-EXIST")).status_code == 404


@pytest.mark.django_db
class TestEquipmentUpdate:
    def test_patch_status(self, auth_client, equipment):
        response = auth_client.patch(
            detail_url(equipment.id),
            {"status": EquipmentStatus.IN_MAINTENANCE},
            format="json",
        )
        assert response.status_code == 200
        equipment.refresh_from_db()
        assert equipment.status == EquipmentStatus.IN_MAINTENANCE

    def test_patch_with_same_asset_tag_no_duplicate_error(self, auth_client, equipment):
        response = auth_client.patch(
            detail_url(equipment.id),
            {"asset_tag": equipment.asset_tag},
            format="json",
        )
        assert response.status_code == 200

    def test_put_replaces_all_fields(self, auth_client, branch, equipment):
        payload = {
            "name": "Reemplazado",
            "asset_tag": "EQ-NEW",
            "brand": "GE",
            "model": "Z1",
            "branch": branch.id,
            "location": "Quirófano",
            "purchase_date": "2024-01-01",
            "status": EquipmentStatus.ACTIVE,
        }
        response = auth_client.put(detail_url(equipment.id), payload, format="json")
        assert response.status_code == 200
        equipment.refresh_from_db()
        assert equipment.asset_tag == "EQ-NEW"
        assert equipment.location == "Quirófano"


@pytest.mark.django_db
class TestEquipmentRegenerateQr:
    def test_regenerate_replaces_file(self, auth_client, equipment):
        storage = equipment.qr_code.storage
        old_path = equipment.qr_code.name
        assert storage.exists(old_path)

        response = auth_client.post(regenerate_url(equipment.id))

        assert response.status_code == 200
        body = response.json()
        assert body["qr_code_url"]
        equipment.refresh_from_db()
        assert storage.exists(equipment.qr_code.name)


@pytest.mark.django_db
class TestEquipmentDelete:
    def test_delete_204_and_removes_qr_file(self, auth_client, equipment):
        storage = equipment.qr_code.storage
        path = equipment.qr_code.name
        response = auth_client.delete(detail_url(equipment.id))
        assert response.status_code == 204
        assert not Equipment.objects.filter(pk=equipment.id).exists()
        assert not storage.exists(path)

    def test_delete_missing_returns_404(self, auth_client):
        assert auth_client.delete(detail_url(99999)).status_code == 404
