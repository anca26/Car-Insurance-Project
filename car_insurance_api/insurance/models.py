from asyncio.windows_events import NULL
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
# Create your models here.

MIN_YEAR, MAX_YEAR = 1900, 2100

class Owner(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return self.name
    
    
class Car(models.Model):
    vin = models.CharField(max_length=17, unique=True) # Vehicle Identification Number
    make = models.CharField(max_length=64, null=True, blank=True) 
    model = models.CharField(max_length=64, null=True, blank=True)
    year_of_manufacture = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(MIN_YEAR), MaxValueValidator(MAX_YEAR)],
    )
    owner = models.ForeignKey(Owner, on_delete=models.PROTECT, related_name="cars")
    

    class Meta:
        indexes = [
            models.Index(fields=['vin'])
        ]
        
    def __str__(self) -> str:
        return f"{self.vin}"
    
class InsurancePolicy(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="policies")
    provider = models.CharField(max_length=128, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    
    logged_expiry_at = models.DateTimeField(null=True, blank=True)
    #for background job
    
    class Meta:
        indexes = [
            models.Index(fields=['car', 'start_date', 'end_date'])
        ]
        constraints = [
        models.CheckConstraint(
            check=models.Q(end_date__gte=models.F("start_date")),
            name="policy_end_after_start"
        )
    ]


    def __str__(self) -> str:
        return f"Policy #{self.pk} for {self.car.vin}"


class Claim(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="claims")
    claim_date = models.DateField()
    description = models.CharField(max_length=512)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)