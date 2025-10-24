from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Create your views here.
@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})