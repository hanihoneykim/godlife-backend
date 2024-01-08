from django.urls import path
from .views import (
    UserSignUp,
    UserLogin,
    MyProfileDetail,
    SocialAuthentication,
)

urlpatterns = [
    path("signup", UserSignUp.as_view()),
    path("login", UserLogin.as_view()),
    path("myprofile", MyProfileDetail.as_view()),
    path("social/<str:provider>", SocialAuthentication.as_view()),
]
