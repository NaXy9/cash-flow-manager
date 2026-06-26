from rest_framework import serializers

from .models import Category, Status, Subcategory, TransactionType


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ["id", "name", "created_at"]
        read_only_fields = ["created_at"]

class TransactionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionType
        fields = ["id", "name", "kind", "created_at"]
        read_only_fields = ["created_at"]

class CategorySerializer(serializers.ModelSerializer):
    transaction_type_name = serializers.CharField(
        source="transaction_type.name", read_only=True
    )
    class Meta:
        model = Category
        fields = ["id", "name", "transaction_type", "transaction_type_name", "created_at"]
        read_only_fields = ["created_at"]


class SubcategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    class Meta:
        model = Subcategory
        fields = ["id", "name", "category", "category_name", "created_at"]
        read_only_fields = ["created_at"]
