from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics, status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from config.permissions import IsLeaderPermission, IsTeamMemberPermission
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

        Member.objects.create(
            user=self.request.user, team=team_instance, is_leader=True
        )


class TeamDetail(generics.RetrieveUpdateDestroyAPIView):
    parser_classes = [MultiPartParser]
    serializer_class = TeamSerializer
    queryset = Team.objects.all()

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsTeamMemberPermission()]
        elif self.request.method == ["PUT", "PATCH", "DELETE"]:
            return [IsLeaderPermission()]

        return super().get_permissions()


class MemberListCreate(generics.ListCreateAPIView):
    serializer_class = MemberSerializer
    queryset = Member.objects.all()

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsTeamMemberPermission()]
        elif self.request.method == "POST":
            return [IsAuthenticated()]

        return super().get_permissions()

    def perform_create(self, serializer):
        team_pk = self.kwargs.get("pk", None)
        team_instance = get_object_or_404(Team, pk=team_pk)
        serializer.save(user=self.request.user, team=team_instance)


class MemberRemove(generics.DestroyAPIView):
    serializer_class = MemberSerializer
    permission_classes = (IsLeaderPermission,)
    queryset = Member.objects.all()

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        user_pk = self.kwargs.get("user_pk")

        member = Member.objects.filter(team=pk, user=user_pk).first()
        if member:
            member.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
