from django.urls import path
from .views import TeamListCreate

urlpatterns = [
    path("teams", TeamListCreate.as_view()),
]
