from rest_framework import serializers
from insurance.models import Owner, Car, InsurancePolicy, Claim


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = ["id", "name", "email"]


class CarSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)
    yearOfManufacture = serializers.IntegerField(source="year_of_manufacture")

    class Meta:
        model = Car
        fields = ["id", "vin", "make", "model", "yearOfManufacture", "owner"]


class InsurancePolicySerializer(serializers.ModelSerializer):
    startDate = serializers.DateField(source="start_date")
    endDate = serializers.DateField(source="end_date")

    class Meta:
        model = InsurancePolicy
        fields = ["id", "provider", "startDate", "endDate"]


class ClaimSerializer(serializers.ModelSerializer):
    claimDate = serializers.DateField(source="claim_date")

    class Meta:
        model = Claim
        fields = ["id", "claimDate", "description", "amount"]
