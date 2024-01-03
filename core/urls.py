from django.urls import path
from .views import TeamListCreate, TeamDetail, MemberListCreate

urlpatterns = [
    path("teams", TeamListCreate.as_view()),
    path("teams/<str:pk>", TeamDetail.as_view()),
    path("teams/<str:pk>/members", MemberListCreate.as_view()),
]
