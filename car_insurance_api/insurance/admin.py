from django.contrib import admin
from insurance.models import Owner,Car,InsurancePolicy,Claim
# Register your models here.
admin.site.register(Owner)
admin.site.register(Car)
admin.site.register(InsurancePolicy)
admin.site.register(Claim)