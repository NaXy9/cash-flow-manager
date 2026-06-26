from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "date", "status", "transaction_type",
        "category", "subcategory", "amount", "created_at",
    ]
    list_filter = ["status", "transaction_type", "category", "date"]
    search_fields = ["comment"]
    date_hierarchy = "date"
    ordering = ["-date"]
