from django.urls import path
from .views import (
    CarListView,
    InsuranceValidityView,
    PolicyCreateView,
    ClaimCreateView,
    CarHistoryView,
)

urlpatterns = [
    path("cars/", CarListView.as_view(), name="cars-list"),
    path("cars/<int:car_id>/insurance-valid/", InsuranceValidityView.as_view(), name="insurance-valid"),
    path("cars/<int:car_id>/policies/",        PolicyCreateView.as_view(),      name="create-policy"),
    path("cars/<int:car_id>/claims/",          ClaimCreateView.as_view(),       name="create-claim"),
    path("cars/<int:car_id>/history/",         CarHistoryView.as_view(),        name="car-history"),
]
