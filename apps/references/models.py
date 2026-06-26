from django.db import models

class Status(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class TransactionType(models.Model):
    INCOME = "income"
    EXPENSE = "expense"
    KIND_CHOICES = [
        (INCOME, "Поступление"),
        (EXPENSE, "Расход"),
    ]
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    kind = models.CharField(
        max_length=10,
        choices=KIND_CHOICES,
        default=INCOME,
        verbose_name="Направление",
        help_text="Определяет смысловое направление типа для аналитики.",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    class Meta:
        verbose_name = "Тип"
        verbose_name_plural = "Типы"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    transaction_type = models.ForeignKey(
        TransactionType,
        on_delete=models.PROTECT,
        related_name="categories",
        verbose_name="Тип транзакции",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["transaction_type__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "transaction_type"],
                name="unique_category_per_type",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.transaction_type})"


class Subcategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="subcategories",
        verbose_name="Категория",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"
        ordering = ["category__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "category"],
                name="unique_subcategory_per_category",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.category.name})"
