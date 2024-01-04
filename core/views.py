from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics, status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from config.permissions import IsLeaderPermission, IsTeamMemberPermission
from rest_framework.parsers import MultiPartParser
from .serializers import LogSerializer, TeamSerializer, CategorySerializer
from user.serializers import MemberSerializer
from .models import Log, Team, Category
from user.models import Member


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

    def create(self, request, pk):
        team_instance = get_object_or_404(Team, pk=pk)

        existing_member = Member.objects.filter(
            user=self.request.user, team=team_instance
        ).exists()
        if existing_member:
            return Response(
                data={"ok": False, "message": "이미 가입된 팀원입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=self.request.user, team=team_instance)
            return Response(
                data={"ok": True, "message": "가입되었습니다."},
                status=status.HTTP_201_CREATED,
            )


# 팀 리더의 멤버 삭제 기능
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


# 팀 멤버의 본인 탈퇴 기능
class TeamLeaveView(generics.DestroyAPIView):
    serializer_class = MemberSerializer
    permission_classes = (IsTeamMemberPermission,)
    queryset = Member.objects.all()

    def delete(self, request, pk):
        team_member = Member.objects.filter(team=pk, user=request.user).first()

        if team_member:
            team_member.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # 사용자가 해당 팀의 멤버가 아닌 경우
            return Response(
                {"detail": "해당 팀의 멤버가 아닙니다."}, status=status.HTTP_403_FORBIDDEN
            )
