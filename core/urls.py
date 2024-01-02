from django.urls import path
from .views import LogListCreate

urlpatterns = [
    path("logs", LogListCreate.as_view()),
]
