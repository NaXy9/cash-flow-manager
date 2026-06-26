from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.references.api_views import (
    StatusViewSet,
    TransactionTypeViewSet,
    CategoryViewSet,
    SubcategoryViewSet,
)
from apps.transactions.api_views import TransactionViewSet

router = DefaultRouter()
router.register("statuses",      StatusViewSet,         basename="api-status")
router.register("types",         TransactionTypeViewSet, basename="api-type")
router.register("categories",    CategoryViewSet,       basename="api-category")
router.register("subcategories", SubcategoryViewSet,    basename="api-subcategory")
router.register("transactions",  TransactionViewSet,    basename="api-transaction")

urlpatterns = [
    path("admin/",   admin.site.urls),
    path("",         include("apps.transactions.urls", namespace="transactions")),
    path("api/v1/",  include(router.urls)),
]
