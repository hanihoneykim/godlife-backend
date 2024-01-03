"""
Permissions such as IsAdminOnly
"""
from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS
from django.conf import settings
from django.core.cache import cache
from user.models import User
from user.models import AuthToken


class IsLeaderPermission(BasePermission):
    def has_permission(self, request, view):
        # 해당 팀의 멤버이면서 리더인지 체크
        team_id = view.kwargs.get("pk")
        return request.user.team_member.filter(team_id=team_id, is_leader=True).exists()


class IsTeamMemberPermission(BasePermission):
    def has_permission(self, request, view):
        # 해당 팀의 멤버인지 체크
        team_id = view.kwargs.get("pk")
        return request.user.team_member.filter(team_id=team_id).exists()
