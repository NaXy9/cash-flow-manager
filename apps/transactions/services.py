from django.core.exceptions import ValidationError

from apps.references.models import Category, Subcategory, TransactionType


def validate_cascade_chain(
    transaction_type: TransactionType,
    category: Category,
    subcategory: Subcategory,
) -> None:
    errors: dict[str, str] = {}

    if category is not None and transaction_type is not None:
        if category.transaction_type_id != transaction_type.pk:
            errors["category"] = (
                f"Категория «{category.name}» не относится к типу "
                f"«{transaction_type.name}». Выберите категорию из "
                f"списка, доступного для данного типа."
            )

    if not errors and subcategory is not None and category is not None:
        if subcategory.category_id != category.pk:
            errors["subcategory"] = (
                f"Подкатегория «{subcategory.name}» не относится к "
                f"категории «{category.name}». Выберите подкатегорию из "
                f"списка, доступного для данной категории."
            )

    if errors:
        raise ValidationError(errors)
