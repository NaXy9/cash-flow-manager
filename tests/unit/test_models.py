import pytest
from decimal import Decimal
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.core.exceptions import ValidationError

from apps.references.models import Category, Status, Subcategory, TransactionType
from apps.transactions.models import Transaction


@pytest.mark.django_db
class TestStatusModel:
    def test_str(self, status):
        assert str(status) == "Бизнес"

    def test_name_unique(self, status):
        with pytest.raises(IntegrityError):
            Status.objects.create(name="Бизнес")

    def test_cannot_delete_if_used_in_transaction(self, transaction, status):
        with pytest.raises(ProtectedError):
            status.delete()


@pytest.mark.django_db
class TestTransactionTypeModel:
    def test_str(self, expense_type):
        assert str(expense_type) == "Списание"

    def test_cannot_delete_if_used_in_transaction(self, transaction, expense_type):
        with pytest.raises(ProtectedError):
            expense_type.delete()


@pytest.mark.django_db
class TestCategoryModel:
    def test_str_includes_type(self, category, expense_type):
        assert "Маркетинг" in str(category)
        assert "Списание" in str(category)

    def test_unique_together_name_and_type(self, db, category, expense_type):
        """Same name under same type → IntegrityError."""
        with pytest.raises(IntegrityError):
            Category.objects.create(name="Маркетинг", transaction_type=expense_type)

    def test_same_name_allowed_in_different_type(self, db, category, income_type):
        """Same name under different type is allowed (unique_together)."""
        cat2 = Category.objects.create(name="Маркетинг", transaction_type=income_type)
        assert cat2.pk != category.pk

    def test_cannot_delete_type_if_category_references_it(self, db, category, expense_type):
        with pytest.raises(ProtectedError):
            expense_type.delete()

    def test_cannot_delete_category_if_transaction_references_it(
        self, transaction, category
    ):
        with pytest.raises(ProtectedError):
            category.delete()


@pytest.mark.django_db
class TestSubcategoryModel:
    def test_str_includes_category(self, subcategory):
        assert "Avito" in str(subcategory)
        assert "Маркетинг" in str(subcategory)

    def test_unique_together_name_and_category(self, db, subcategory, category):
        with pytest.raises(IntegrityError):
            Subcategory.objects.create(name="Avito", category=category)

    def test_cannot_delete_category_if_subcategory_references_it(
        self, db, subcategory, category
    ):
        with pytest.raises(ProtectedError):
            category.delete()


@pytest.mark.django_db
class TestTransactionModel:
    def test_str_format(self, transaction):
        s = str(transaction)
        assert "Списание" in s
        assert "₽" in s

    def test_amount_must_be_positive(
        self, db, status, expense_type, category, subcategory
    ):
        t = Transaction(
            date=__import__("datetime").date.today(),
            status=status,
            transaction_type=expense_type,
            category=category,
            subcategory=subcategory,
            amount=Decimal("0.00"),
        )
        with pytest.raises(ValidationError):
            t.full_clean()

    def test_comment_is_optional(
        self, db, status, expense_type, category, subcategory
    ):
        from datetime import date
        t = Transaction.objects.create(
            date=date.today(),
            status=status,
            transaction_type=expense_type,
            category=category,
            subcategory=subcategory,
            amount=Decimal("100.00"),
        )
        assert t.comment == ""

    def test_cannot_delete_subcategory_if_transaction_references_it(
        self, transaction, subcategory
    ):
        with pytest.raises(ProtectedError):
            subcategory.delete()
