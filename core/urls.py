from django.urls import path
from .views import (
    TeamListCreate,
    TeamDetail,
    MemberListCreate,
    MemberRemove,
    TeamLeaveView,
    CategoryListCreate,
    CategoryDetail,
    LogListCreate,
    LogDetail,
)

urlpatterns = [
    path("teams", TeamListCreate.as_view()),
    path("teams/<str:pk>", TeamDetail.as_view()),
    path("teams/<str:pk>/members", MemberListCreate.as_view()),
    path("teams/<str:pk>/members/leave", TeamLeaveView.as_view()),
    path("teams/<str:pk>/members/<str:user_pk>/remove", MemberRemove.as_view()),
    path("teams/<str:pk>/categories", CategoryListCreate.as_view()),
    path("teams/<str:pk>/categories/<str:category_pk>", CategoryDetail.as_view()),
    path("teams/<str:pk>/categories/<str:category_pk>/logs", LogListCreate.as_view()),
    path(
        "teams/<str:pk>/categories/<str:category_pk>/logs/<str:log_pk>",
        LogDetail.as_view(),
    ),
]
