import pytest
from datetime import date
from decimal import Decimal

from apps.references.models import Category, Status, Subcategory, TransactionType
from apps.transactions.models import Transaction


@pytest.fixture
def status(db):
    return Status.objects.create(name="Бизнес")


@pytest.fixture
def income_type(db):
    return TransactionType.objects.create(name="Пополнение", kind=TransactionType.INCOME)


@pytest.fixture
def expense_type(db):
    return TransactionType.objects.create(name="Списание", kind=TransactionType.EXPENSE)


@pytest.fixture
def category(db, expense_type):
    return Category.objects.create(name="Маркетинг", transaction_type=expense_type)


@pytest.fixture
def other_category(db, income_type):
    """Category that belongs to a DIFFERENT type — used to test cascade violations."""
    return Category.objects.create(name="Выручка", transaction_type=income_type)


@pytest.fixture
def subcategory(db, category):
    return Subcategory.objects.create(name="Avito", category=category)


@pytest.fixture
def other_subcategory(db, other_category):
    """Subcategory of other_category — used to test cascade violations."""
    return Subcategory.objects.create(name="Интернет-магазин", category=other_category)


@pytest.fixture
def transaction(db, status, expense_type, category, subcategory):
    return Transaction.objects.create(
        date=date.today(),
        status=status,
        transaction_type=expense_type,
        category=category,
        subcategory=subcategory,
        amount=Decimal("1500.00"),
        comment="Test transaction",
    )
