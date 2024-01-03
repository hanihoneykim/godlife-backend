from django.urls import path
from .views import TeamListCreate, TeamDetail

urlpatterns = [
    path("teams", TeamListCreate.as_view()),
    path("teams/<str:pk>", TeamDetail.as_view()),
]
