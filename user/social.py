import requests
from django.conf import settings
from django.contrib.auth import get_user_model

KAKAO_REST_API_KEY = settings.KAKAO_REST_API_KEY
USER_MODEL = get_user_model()


def kakao_get_access_token(data):
    redirect_uri = data.get("redirect_uri")
    code = data.get("code")
    if not code:
        raise ValueError("code is required")
    url = "https://kauth.kakao.com/oauth/token"
    headers = {"Content-type": "application/x-www-form-urlencoded; charset=utf-8"}

    body = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_REST_API_KEY,
        "redirect_uri": redirect_uri,
        "code": code,
    }
    kakao_token_response = requests.post(url, headers=headers, data=body)
    kakao_token_response = kakao_token_response.json()
    error = kakao_token_response.get("error", None)
    if error:
        return None

    access_token = kakao_token_response.get("access_token")
    print(access_token)
    return access_token


def kakao_get_user(access_token=None):
    if not access_token:
        return None
    url = "https://kapi.kakao.com/v2/user/me"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-type": "application/x-www-form-urlencoded; charset=utf-8",
    }

    kakao_response = requests.post(url, headers=headers)
    kakao_response = kakao_response.json()
    user, _ = USER_MODEL.objects.get_or_create(
        social_provider="kakao", social_uid=kakao_response["id"]
    )
    if kakao_account := kakao_response.get("kakao_account"):
        # user.nickname = kakao_account.get('nickname')
        # user.email = kakao_account.get('email')
        user.save()
    user.nickname = kakao_response.get("id")
    return user


def naver_get_access_token(data):
    code = data.get("code")
    state = data.get("state")
    client_id = settings.NAVER_CLIENT_ID
    client_secret = settings.NAVER_CLIENT_SECRET
    redirect_uri = "https://127.0.0.1/auth/naver"

    response = requests.get(
        f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&code={code}&state={state}"
    )
    response = response.json()
    print(response)
    error = response.get("error")
    if error:
        return None
    access_token = response.get("access_token")
    return access_token


def naver_get_user(access_token=None):
    if not access_token:
        return None
    header = "Bearer " + access_token
    print("access token: ", access_token)

    url = "https://openapi.naver.com/v1/nid/me"
    headers = {"Authorization": header}
    naver_response = requests.get(url, headers=headers)
    response = naver_response.json()

    print(response["response"])
    naver_response = response["response"]
    email = naver_response.get("email", None)
    if not email:
        # create random hex email
        email = f"{naver_response['id']}@naver.com"
    user, _ = USER_MODEL.objects.get_or_create(
        social_provider="kakao", social_uid=naver_response["id"]
    )
    user.nickname = naver_response.get("nickname")
    user.email = naver_response.get("email", None)
    user.save()
    return user
