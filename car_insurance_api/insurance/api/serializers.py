from rest_framework import serializers
from insurance.models import Owner, Car, InsurancePolicy, Claim


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = "__all__"


class CarSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)
    yearOfManufacture = serializers.IntegerField(source="year_of_manufacture")

    class Meta:
        model = Car
        fields = "__all__"


class InsurancePolicySerializer(serializers.ModelSerializer):
    startDate = serializers.DateField(source="start_date")
    endDate = serializers.DateField(source="end_date")

    class Meta:
        model = InsurancePolicy
        exclude = ["car","start_date","end_date"]


class ClaimSerializer(serializers.ModelSerializer):
    claimDate = serializers.DateField(source="claim_date")

    class Meta:
        model = Claim
        exclude = ["car","claim_date"]
        
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value
