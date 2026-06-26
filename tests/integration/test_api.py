"""
Covers:
  - Cascade endpoints: /api/v1/types/{id}/categories/
                       /api/v1/categories/{id}/subcategories/
  - Transaction ViewSet: create, retrieve, update, delete
  - Cascade validation at the API layer (serializer)
  - 409 Conflict on protected delete
"""
import pytest
from decimal import Decimal
from datetime import date

from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture
def api():
    return APIClient()


@pytest.mark.django_db
class TestCascadeEndpoints:

    def test_categories_for_type(
        self, api, expense_type, category
    ):
        url = f"/api/v1/types/{expense_type.pk}/categories/"
        resp = api.get(url)
        assert resp.status_code == 200
        names = [c["name"] for c in resp.json()]
        assert "Маркетинг" in names

    def test_categories_for_type_empty_when_no_categories(
        self, api, income_type
    ):
        url = f"/api/v1/types/{income_type.pk}/categories/"
        resp = api.get(url)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_subcategories_for_category(
        self, api, category, subcategory
    ):
        url = f"/api/v1/categories/{category.pk}/subcategories/"
        resp = api.get(url)
        assert resp.status_code == 200
        names = [s["name"] for s in resp.json()]
        assert "Avito" in names

    def test_unknown_type_returns_404(self, api):
        resp = api.get("/api/v1/types/99999/categories/")
        assert resp.status_code == 404


@pytest.mark.django_db
class TestTransactionAPI:

    def _payload(self, status, expense_type, category, subcategory):
        return {
            "date": str(date.today()),
            "status": status.pk,
            "transaction_type": expense_type.pk,
            "category": category.pk,
            "subcategory": subcategory.pk,
            "amount": "2500.00",
            "comment": "API test",
        }

    def test_create_transaction(
        self, api, status, expense_type, category, subcategory
    ):
        payload = self._payload(status, expense_type, category, subcategory)
        resp = api.post("/api/v1/transactions/", payload, format="json")
        assert resp.status_code == 201
        assert Decimal(resp.json()["amount"]) == Decimal("2500.00")

    def test_create_rejects_future_date(
        self, api, status, expense_type, category, subcategory
    ):
        payload = self._payload(status, expense_type, category, subcategory)
        payload["date"] = "2099-01-01"
        resp = api.post("/api/v1/transactions/", payload, format="json")
        assert resp.status_code == 400
        assert "date" in resp.json()

    def test_create_rejects_zero_amount(
        self, api, status, expense_type, category, subcategory
    ):
        payload = self._payload(status, expense_type, category, subcategory)
        payload["amount"] = "0.00"
        resp = api.post("/api/v1/transactions/", payload, format="json")
        assert resp.status_code == 400

    def test_create_rejects_wrong_category_for_type(
        self, api, status, expense_type, other_category, subcategory
    ):
        payload = {
            "date": str(date.today()),
            "status": status.pk,
            "transaction_type": expense_type.pk,
            "category": other_category.pk,
            "subcategory": subcategory.pk,
            "amount": "100.00",
        }
        resp = api.post("/api/v1/transactions/", payload, format="json")
        assert resp.status_code == 400
        assert "category" in resp.json()

    def test_create_rejects_wrong_subcategory_for_category(
        self, api, status, expense_type, category, other_subcategory
    ):
        payload = {
            "date": str(date.today()),
            "status": status.pk,
            "transaction_type": expense_type.pk,
            "category": category.pk,
            "subcategory": other_subcategory.pk,
            "amount": "100.00",
        }
        resp = api.post("/api/v1/transactions/", payload, format="json")
        assert resp.status_code == 400
        assert "subcategory" in resp.json()

    def test_retrieve_transaction(self, api, transaction):
        resp = api.get(f"/api/v1/transactions/{transaction.pk}/")
        assert resp.status_code == 200
        assert resp.json()["id"] == transaction.pk

    def test_update_transaction(self, api, transaction):
        resp = api.patch(
            f"/api/v1/transactions/{transaction.pk}/",
            {"comment": "updated comment"},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.json()["comment"] == "updated comment"

    def test_delete_transaction(self, api, transaction):
        resp = api.delete(f"/api/v1/transactions/{transaction.pk}/")
        assert resp.status_code == 204

    def test_list_transactions(self, api, transaction):
        resp = api.get("/api/v1/transactions/")
        assert resp.status_code == 200
        data = resp.json()
        items = data["results"] if isinstance(data, dict) else data
        assert len(items) >= 1


@pytest.mark.django_db
class TestReferenceProtectedDelete:

    def test_delete_status_used_in_transaction_returns_409(
        self, api, transaction, status
    ):
        resp = api.delete(f"/api/v1/statuses/{status.pk}/")
        assert resp.status_code == 409
        assert "detail" in resp.json()

    def test_delete_type_used_in_transaction_returns_409(
        self, api, transaction, expense_type
    ):
        resp = api.delete(f"/api/v1/types/{expense_type.pk}/")
        assert resp.status_code == 409

    def test_delete_category_used_in_transaction_returns_409(
        self, api, transaction, category
    ):
        resp = api.delete(f"/api/v1/categories/{category.pk}/")
        assert resp.status_code == 409

    def test_delete_unused_status_succeeds(self, api, db):
        from apps.references.models import Status
        s = Status.objects.create(name="Временный")
        resp = api.delete(f"/api/v1/statuses/{s.pk}/")
        assert resp.status_code == 204
