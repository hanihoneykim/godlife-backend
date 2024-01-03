from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser
from .serializers import LogSerializer, TeamSerializer
from user.serializers import MemberSerializer
from .models import Log, Team
from user.models import Member


class LogListCreate(generics.ListCreateAPIView):
    parser_classes = [MultiPartParser]
    serializer_class = LogSerializer
    permission_classes = [AllowAny]
    queryset = Log.objects.all()


class TeamListCreate(generics.ListCreateAPIView):
    parser_classes = [MultiPartParser]
    serializer_class = TeamSerializer
    queryset = Team.objects.all()

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        elif self.request.method == "POST":
            return [IsAuthenticated()]

        return super().get_permissions()

    def perform_create(self, serializer):
        team_instance = serializer.save()

        # request.user를 해당 팀의 멤버로 생성, is_leader=True
        user = self.request.user
        member_data = {"user": user, "team": team_instance, "is_leader": True}
        member_serializer = MemberSerializer(data=member_data)
        member_serializer.is_valid(raise_exception=True)
        member_serializer.save()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
