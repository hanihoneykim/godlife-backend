import uuid
from django.db import models
from config.utils import compress_image, upload_path
from common.models import CommonModel


class Team(CommonModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False, blank=False)
    name = models.CharField(max_length=30, null=False, blank=False)
    description = models.CharField(max_length=300, null=False, blank=False)
    image = models.ImageField(null=True, blank=True, upload_to=upload_path)


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False, blank=False)
    name = models.CharField(max_length=30, null=False, blank=False)
    team = models.ForeignKey(
        Team, related_name="categories", null=True, on_delete=models.CASCADE
    )


class Log(CommonModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False, blank=False)
    user = models.ForeignKey(
        "user.User", null=True, related_name="logs", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=50, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to=upload_path)
    category = models.ForeignKey(
        Category, related_name="logs", null=True, on_delete=models.CASCADE
    )
    liked_user = models.ManyToManyField(
        "user.User", related_name="liked_logs", null=True, blank=True
    )

    def save(self, *args, **kwargs):
        if self.pk and self.image:
            try:
                original = Log.objects.get(pk=self.pk)
                if original.image != self.image:
                    self.image = compress_image(self.image, size=(500, 500))
            except Log.DoesNotExist:
                self.image = compress_image(self.image, size=(500, 500))
            except:
                pass
        super().save(*args, **kwargs)


class Comment(CommonModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False, blank=False)
    user = models.ForeignKey(
        "user.User", null=True, related_name="comments", on_delete=models.CASCADE
    )
    comment = models.TextField(null=True, blank=True)
    log = models.ForeignKey(
        Log, related_name="comments", null=True, on_delete=models.CASCADE
    )
