import django_filters
from django import forms

from apps.references.models import Category, Status, Subcategory, TransactionType

from .models import Transaction

_DATE_WIDGET = forms.DateInput(attrs={"type": "date", "class": "form-control"})
_SELECT_WIDGET = forms.Select(attrs={"class": "form-select"})


class TransactionFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(
        field_name="date",
        lookup_expr="gte",
        label="Дата с",
        widget=_DATE_WIDGET,
    )
    date_to = django_filters.DateFilter(
        field_name="date",
        lookup_expr="lte",
        label="Дата по",
        widget=_DATE_WIDGET,
    )
    status = django_filters.ModelChoiceFilter(
        queryset=Status.objects.all(),
        label="Статус",
        empty_label="Все статусы",
        widget=_SELECT_WIDGET,
    )
    transaction_type = django_filters.ModelChoiceFilter(
        queryset=TransactionType.objects.all(),
        label="Тип",
        empty_label="Все типы",
        widget=_SELECT_WIDGET,
    )
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.select_related("transaction_type").all(),
        label="Категория",
        empty_label="Все категории",
        widget=_SELECT_WIDGET,
    )
    subcategory = django_filters.ModelChoiceFilter(
        queryset=Subcategory.objects.select_related("category").all(),
        label="Подкатегория",
        empty_label="Все подкатегории",
        widget=_SELECT_WIDGET,
    )

    class Meta:
        model = Transaction
        fields = [
            "date_from",
            "date_to",
            "status",
            "transaction_type",
            "category",
            "subcategory",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.form.fields.values():
            if not isinstance(f.widget, forms.Select):
                f.widget.attrs.setdefault("class", "form-control")
