from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from insurance.models import Car, InsurancePolicy, Claim
from insurance.api.serializers import CarSerializer, InsurancePolicySerializer, ClaimSerializer

import structlog
log = structlog.get_logger()


class CarListView(generics.ListAPIView):
    queryset = Car.objects.select_related("owner").all()
    serializer_class = CarSerializer


class CarLookupMixin:
    lookup_url_kwarg = "car_id"

    def get_car(self) -> Car:
        car_id = self.kwargs.get(self.lookup_url_kwarg)
        return get_object_or_404(Car, pk=car_id)


class InsuranceValidityView(CarLookupMixin, APIView):
    def get(self, request, *args, **kwargs):
        car = self.get_car()
        date_str = request.query_params.get("date")
        if not date_str:
            return Response({"detail": "Query param 'date' is required"}, status=status.HTTP_400_BAD_REQUEST400)

        try:
            check_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"detail": "Date must be YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST400)

        if not (1900 <= check_date.year <= 2100):
            return Response({"detail": "Date out of range (1900–2100)"}, status=status.HTTP_400_BAD_REQUEST400)

        valid = InsurancePolicy.objects.filter(
            car=car,
            start_date__lte=check_date,
            end_date__gte=check_date,
        ).exists()

        return Response({"carId": car.id, "date": check_date.isoformat(), "valid": valid})

class PolicyCreateView(CarLookupMixin, generics.CreateAPIView):
    serializer_class = InsurancePolicySerializer

    def perform_create(self, serializer):
        start_date = serializer.validated_data["start_date"]
        end_date = serializer.validated_data["end_date"]
        if end_date < start_date:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"endDate": "endDate must be >= startDate"})

        serializer.save(car=self.get_car())
        car = self.get_car()
        log.info("Policy created", car_id=car.id)


class ClaimCreateView(CarLookupMixin, generics.CreateAPIView):
    serializer_class = ClaimSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        #Location header: /api/cars/{carId}/claims/{id}
        car = self.get_car()
        claim_id = response.data.get("id")
        response["Location"] = f"/api/cars/{car.id}/claims/{claim_id}"
        log.info("Claim created", car_id=car.id, claim_id=claim_id)
        return response

    def perform_create(self, serializer):
        serializer.save(car=self.get_car())


class CarHistoryView(CarLookupMixin, APIView):
    def get(self, request, *args, **kwargs):
        car = self.get_car()
        events = []
        # policies
        for p in car.policies.all():
            events.append({
                "type": "POLICY",
                "policyId": p.id,
                "startDate": p.start_date.isoformat(),
                "endDate": p.end_date.isoformat(),
                "provider": p.provider,
            })
        # claims
        for c in car.claims.all():
            events.append({
                "type": "CLAIM",
                "claimId": c.id,
                "claimDate": c.claim_date.isoformat(),
                "amount": float(c.amount),
                "description": c.description,
            })
        events.sort(key=lambda e: e.get("startDate") or e.get("claimDate"))
        return Response(events)
