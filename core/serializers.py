from rest_framework import serializers
from core.models import Log, Team


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = "__all__"
        read_only_fields = ("id",)


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = "__all__"
        read_only_fields = ("id",)
