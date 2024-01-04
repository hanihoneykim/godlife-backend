from django.urls import path
from .views import (
    UserSignUp,
    UserLogin,
    MyProfileDetail,
)

urlpatterns = [
    path("signup", UserSignUp.as_view()),
    path("login", UserLogin.as_view()),
    path("myprofile", MyProfileDetail.as_view()),
]
