from datetime import date

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Transaction
from .services import validate_cascade_chain


class TransactionSerializer(serializers.ModelSerializer):
    # Read-only convenience fields for display
    status_name = serializers.CharField(source="status.name", read_only=True)
    type_name = serializers.CharField(source="transaction_type.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    subcategory_name = serializers.CharField(source="subcategory.name", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "date",
            "status",
            "status_name",
            "transaction_type",
            "type_name",
            "category",
            "category_name",
            "subcategory",
            "subcategory_name",
            "amount",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    # Field-level validation

    def validate_date(self, value):
        """Date must not be in the future."""
        if value > date.today():
            raise serializers.ValidationError(
                "Дата не может быть в будущем."
            )
        return value

    def validate_amount(self, value):
        """Amount must be strictly positive."""
        if value <= 0:
            raise serializers.ValidationError(
                "Сумма должна быть больше нуля."
            )
        return value

    # Cross-field validation — cascade consistency

    def validate(self, attrs):
        try:
            validate_cascade_chain(
                transaction_type=attrs.get("transaction_type"),
                category=attrs.get("category"),
                subcategory=attrs.get("subcategory"),
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from exc
        return attrs
