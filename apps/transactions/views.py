from decimal import Decimal

from django.db.models import Sum
from django.views.generic import ListView

from apps.references.models import (
    Category,
    Status,
    Subcategory,
    TransactionType,
)

from .filters import TransactionFilter
from .models import Transaction


class TransactionListView(ListView):
    model = Transaction
    template_name = "transactions/list.html"
    context_object_name = "transactions"
    paginate_by = 7

    def get_queryset(self):
        qs = Transaction.objects.select_related(
            "status", "transaction_type", "category", "subcategory"
        )
        self.filterset = TransactionFilter(self.request.GET, queryset=qs)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        filtered_qs = self.filterset.qs

        # Stat cards: use kind field — no fragile string matching
        income_total = (
            filtered_qs
            .filter(transaction_type__kind=TransactionType.INCOME)
            .aggregate(t=Sum("amount"))["t"] or Decimal("0")
        )
        expense_total = (
            filtered_qs
            .filter(transaction_type__kind=TransactionType.EXPENSE)
            .aggregate(t=Sum("amount"))["t"] or Decimal("0")
        )

        # Fetch reference lists once and reuse for both display and counts
        # to avoid redundant COUNT queries per reference table.
        statuses   = list(Status.objects.all())
        types      = list(TransactionType.objects.all())
        categories = list(Category.objects.select_related("transaction_type").all())
        subcats    = list(Subcategory.objects.select_related("category").all())

        ctx.update(
            {
                "filterset": self.filterset,
                "total_count": filtered_qs.count(),
                "income_total": income_total,
                "expense_total": expense_total,
                "balance": income_total - expense_total,
                # Reference data for formModal and dirModal
                "all_statuses":      statuses,
                "all_types":         types,
                "all_categories":    categories,
                "all_subcategories": subcats,
                # Badge counts derived from already-fetched lists (0 extra queries)
                "status_count":      len(statuses),
                "type_count":        len(types),
                "category_count":    len(categories),
                "subcategory_count": len(subcats),
            }
        )
        return ctx
