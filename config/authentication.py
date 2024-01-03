from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from user.models import User, AuthToken
from django.core.cache import cache


class TokenAuthentication(BaseAuthentication):

    """
    Requires a Authorization header with either formats: "Bearer <token>" / "Token <token>"
    Using Cookies also works: "token: <token>"
    You can also send the token in the query string (NOT RECOMMENDED): "?token=<token>"
    Token is handled on this order: Authorization header > Cookie > QueryString
    """

    def authenticate(self, request):
        if request.META.get("HTTP_AUTHORIZATION") and request.META[
            "HTTP_AUTHORIZATION"
        ].split()[0] in ["Token", "Bearer"]:
            token = request.META["HTTP_AUTHORIZATION"].split()[1]
        elif request.COOKIES.get("token"):
            token = request.COOKIES["token"]
        elif request.GET.get("token"):
            token = request.GET["token"]
        else:
            return None
        try:
            cache_key = f"USER_AUTHTOKEN_{token}"
            user_id = cache.get(cache_key, None)
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    return (user, token)
                except:
                    cache.delete(cache_key)
                    return None
            user = AuthToken.objects.get(id=token).user
            cache.set(cache_key, str(user.id), 24 * 60 * 60)
            return (user, token)
        except AuthToken.DoesNotExist:
            return None
        except:
            return None
