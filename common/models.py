from django.db import models


class CommonModel(models.Model):
    """Common Model Definition"""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성시간")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정됨")

    class Meta:
        abstract = True
