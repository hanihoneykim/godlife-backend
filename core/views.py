from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser
from .serializers import LogSerializer
from .models import Log


class LogListCreate(generics.ListCreateAPIView):
    parser_classes = [MultiPartParser]
    serializer_class = LogSerializer
    permission_classes = [AllowAny]
    queryset = Log.objects.all()
