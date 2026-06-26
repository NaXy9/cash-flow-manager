from django.db.models import ProtectedError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Status, Subcategory, TransactionType
from .serializers import (
    CategorySerializer,
    StatusSerializer,
    SubcategorySerializer,
    TransactionTypeSerializer,
)


class ProtectedDestroyMixin:
    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {
                    "detail": (
                        "Невозможно удалить: запись используется в других данных. "
                        "Сначала удалите или переназначьте все связанные элементы."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )


class StatusViewSet(ProtectedDestroyMixin, viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer


class TransactionTypeViewSet(ProtectedDestroyMixin, viewsets.ModelViewSet):
    queryset = TransactionType.objects.all()
    serializer_class = TransactionTypeSerializer

    @action(detail=True, methods=["get"], url_path="categories")
    def categories(self, request, pk=None) -> Response:
        # Return all categories that belong to this transaction type.
        transaction_type = self.get_object()
        qs = Category.objects.filter(
            transaction_type=transaction_type
        ).order_by("name")
        return Response(CategorySerializer(qs, many=True).data)


class CategoryViewSet(ProtectedDestroyMixin, viewsets.ModelViewSet):
    queryset = Category.objects.select_related("transaction_type").all()
    serializer_class = CategorySerializer

    @action(detail=True, methods=["get"], url_path="subcategories")
    def subcategories(self, request, pk=None) -> Response:
        # Return all subcategories that belong to this category.
        category = self.get_object()
        qs = Subcategory.objects.filter(category=category).order_by("name")
        return Response(SubcategorySerializer(qs, many=True).data)


class SubcategoryViewSet(ProtectedDestroyMixin, viewsets.ModelViewSet):
    queryset = Subcategory.objects.select_related("category__transaction_type").all()
    serializer_class = SubcategorySerializer
