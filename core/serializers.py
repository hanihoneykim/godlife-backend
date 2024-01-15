from rest_framework import serializers
from core.models import Log, Team, Category, Comment, ConceptImage


class LogSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)
    user_profile_image = serializers.ImageField(
        source="user.profile_image", read_only=True
    )
    liked_user_count = serializers.SerializerMethodField()

    class Meta:
        model = Log
        fields = "__all__"
        read_only_fields = ("id",)

    def get_liked_user_count(self, obj):
        return obj.liked_user.count()


class TeamSerializer(serializers.ModelSerializer):
    concept_image_name = serializers.CharField(
        source="concept_image.name", read_only=True
    )
    concept_image_image = serializers.CharField(
        source="concept_image.image.url", read_only=True
    )

    class Meta:
        model = Team
        fields = "__all__"
        read_only_fields = ("id",)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ("id",)


class CommentSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)
    user_profile_image = serializers.ImageField(
        source="user.profile_image", read_only=True
    )

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ("id",)


class ConceptImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConceptImage
        fields = "__all__"
        read_only_fields = ("id",)
