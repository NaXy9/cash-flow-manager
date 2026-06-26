from django.contrib import admin

from .models import Category, Status, Subcategory, TransactionType

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]


@admin.register(TransactionType)
class TransactionTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "transaction_type", "created_at"]
    list_filter = ["transaction_type"]
    search_fields = ["name"]


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "created_at"]
    list_filter = ["category__transaction_type", "category"]
    search_fields = ["name"]
