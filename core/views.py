from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from config.permissions import IsLeaderPermission, IsTeamMemberPermission
from rest_framework.parsers import MultiPartParser
from .serializers import (
    LogSerializer,
    TeamSerializer,
    CategorySerializer,
    CommentSerializer,
)
from user.serializers import MemberSerializer
from .models import Log, Team, Category, Comment
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

            # 해당 팀과 유저에 해당하는 로그들 삭제
            logs_to_delete = Log.objects.filter(category__team=pk, user=user_pk)
            logs_to_delete.delete()

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
            # 해당 팀에 본인이 작성한 로그들 삭제
            logs_to_delete = Log.objects.filter(category__team=pk, user=request.user)
            logs_to_delete.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # 사용자가 해당 팀의 멤버가 아닌 경우
            return Response(
                {"detail": "해당 팀의 멤버가 아닙니다."}, status=status.HTTP_403_FORBIDDEN
            )


class CategoryListCreate(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsTeamMemberPermission()]
        elif self.request.method == "POST":
            return [IsLeaderPermission()]

    def create(self, request, pk):
        team_instance = get_object_or_404(Team, pk=pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(team=team_instance)
        return Response(
            data={"ok": True},
            status=status.HTTP_201_CREATED,
        )


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsLeaderPermission]

    def get_object(self):
        pk = self.kwargs.get("pk")
        category_pk = self.kwargs.get("category_pk")
        qs = Category.objects.get(team__id=pk, id=category_pk)
        return qs


class LogListCreate(generics.ListCreateAPIView):
    permission_classes = [IsTeamMemberPermission]
    serializer_class = LogSerializer

    def get_queryset(self):
        team_pk = self.kwargs.get("pk")
        category_pk = self.kwargs.get("category_pk")
        category = Category.objects.get(team__id=team_pk, id=category_pk)
        return Log.objects.filter(category=category)

    def create(self, request, *args, **kwargs):
        team_pk = self.kwargs.get("pk")
        category_pk = self.kwargs.get("category_pk")

        category = get_object_or_404(Category, team__id=team_pk, id=category_pk)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, category=category)
        return Response(
            status=status.HTTP_201_CREATED,
            data={
                "ok": True,
                "data": serializer.data,
            },
        )


class LogDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LogSerializer
    permission_classes = [IsTeamMemberPermission]

    def get_object(self):
        team_pk = self.kwargs.get("pk")
        category_pk = self.kwargs.get("category_pk")
        log_pk = self.kwargs.get("log_pk")
        category = Category.objects.get(team__id=team_pk, id=category_pk)
        log = Log.objects.get(category=category, id=log_pk)
        return log

    def update(self, request, *args, **kwargs):
        log = self.get_object()

        if log.user != request.user:
            raise PermissionDenied("해당 게시글의 작성자가 아닙니다.")

        log.title = request.data.get("title", log.title)
        log.content = request.data.get("content", log.content)
        log.image = request.data.get("image", log.image)
        log.save()

        serializer = self.get_serializer(log)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        log = self.get_object()

        if log.user != request.user:
            raise PermissionDenied("해당 게시글의 작성자가 아닙니다.")

        log.delete()
        return Response({"message": "게시글이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)


class LikeLog(APIView):
    permission_classes = [IsTeamMemberPermission]

    def put(self, request, pk, log_pk):
        log = Log.objects.get(id=log_pk)
        user = request.user
        if user in log.liked_user.all():
            pass
        else:
            log.liked_user.add(user)
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, pk, log_pk):
        log = Log.objects.get(id=log_pk)
        user = request.user
        if user in log.liked_user.all():
            log.liked_user.remove(user)
        else:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentListCreate(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsTeamMemberPermission]

    def get_queryset(self):
        log_pk = self.kwargs.get("log_pk")
        log = Log.objects.get(id=log_pk)
        return Comment.objects.filter(log=log)

    def create(self, request, *args, **kwargs):
        team_pk = self.kwargs.get("team_pk")
        log_pk = self.kwargs.get("log_pk")

        log = get_object_or_404(Log, id=log_pk)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, log=log)
        return Response(
            status=status.HTTP_201_CREATED,
            data={
                "ok": True,
                "data": serializer.data,
            },
        )


class CommentDetail(generics.RetrieveDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsTeamMemberPermission]

    def get_object(self):
        log_pk = self.kwargs.get("log_pk")
        comment_pk = self.kwargs.get("comment_pk")
        try:
            comment = Comment.objects.get(log__id=log_pk, id=comment_pk)
            return comment
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        comment = self.get_object()

        if comment.user != request.user:
            raise PermissionDenied("해당 게시글의 작성자가 아닙니다.")

        comment.delete()
        return Response({"message": "게시글이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
