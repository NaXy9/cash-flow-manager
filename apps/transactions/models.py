from datetime import date
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.references.models import Category, Status, Subcategory, TransactionType


class Transaction(models.Model):
    # Core fields
    date = models.DateField(
        default=date.today,
        verbose_name="Дата",
        help_text="Дата операции (не может быть в будущем).",
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name="transactions",
        verbose_name="Статус",
    )
    transaction_type = models.ForeignKey(
        TransactionType,
        on_delete=models.PROTECT,
        related_name="transactions",
        verbose_name="Тип",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="transactions",
        verbose_name="Категория",
    )
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.PROTECT,
        related_name="transactions",
        verbose_name="Подкатегория",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Сумма (руб.)",
    )
    comment = models.TextField(
        blank=True,
        default="",
        verbose_name="Комментарий",
        help_text="Необязательный комментарий в свободной форме.",
    )

    # Audit timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Запись создана",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Запись обновлена",
    )

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
        ordering = ["-date", "-created_at"]

    def __str__(self) -> str:
        return (
            f"{self.date.strftime('%d.%m.%Y')} | "
            f"{self.transaction_type} | "
            f"{self.amount:,.2f} ₽"
        )
