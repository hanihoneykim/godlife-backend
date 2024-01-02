import uuid
from django.db import models
from config.utils import compress_image, upload_path
from common.models import CommonModel
from user.models import User


class Team(CommonModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False, blank=False)
    name = models.CharField(max_length=30, null=False, blank=False)
    description = models.CharField(max_length=300, null=False, blank=False)
    image = models.ImageField(null=True, blank=True, upload_to=upload_path)
    leader = models.ForeignKey(
        User, null=True, related_name="team", on_delete=models.CASCADE
    )


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False, blank=False)
    name = models.CharField(max_length=30, null=False, blank=False)
