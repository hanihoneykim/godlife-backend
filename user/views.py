from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password
from .models import User, AuthToken
from .serializers import UserSerializer, UserProfileSerializer


class UserSignUp(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        """
        create user using UserSerializer, save hashed password, and return token
        """
        # 기입한 정보가 이미 존재하는 경우 오류 메세지 주기
        if User.objects.filter(email=request.data["email"]).exists():
            return Response(
                data={"status": "FAILED", "message": "이미 존재하는 이메일입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.filter(nickname=request.data["nickname"]).exists():
            return Response(
                data={"status": "FAILED", "message": "이미 존재하는 닉네임입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = serializer.instance
        token = AuthToken.objects.create(user=user)
        user.set_password(request.data.get("password"))
        user.save()
        return Response(
            {"id": str(user.id), "token": str(token.id)}, status=status.HTTP_201_CREATED
        )


class UserLogin(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        try:
            user = User.objects.get(email=email.strip().lower())
        except User.DoesNotExist:
            return Response(
                {"error": "존재하지 않는 유저거나 비밀번호가 맞지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.check_password(password):
            token = AuthToken.objects.create(user=user)
            serializer = UserSerializer(user)
            return Response(
                {"token": str(token.id), "info": serializer.data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "존재하지 않는 유저거나 비밀번호가 맞지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MyProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        print(serializer.is_valid())
        if serializer.is_valid():
            if request.data.get("nickname"):
                if (
                    User.objects.filter(nickname=request.data.get("nickname"))
                    and request.data.get("nickname") != request.user.nickname
                ):
                    return Response(
                        {"error": "이미 존재하는 닉네임입니다."}, status=status.HTTP_400_BAD_REQUEST
                    )
            if request.data.get("old_password"):
                old_password = request.data.get("old_password")

                # Verify old password
                print(old_password)
                print(user.password)
                print(check_password(old_password, user.password))
                if old_password and check_password(old_password, user.password):
                    # If old password is correct, update to the new password
                    new_password = request.data.get("new_password")
                    user.set_password(new_password)
                else:
                    return Response(
                        {"ok": False, "error": "기존 비밀번호를 확인해주세요."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
