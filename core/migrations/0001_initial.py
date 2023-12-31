# Generated by Django 5.0 on 2024-01-02 09:22

import config.utils
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Team",
            fields=[
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="작성시간"),
                ),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정됨")),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.CharField(max_length=30)),
                ("description", models.CharField(max_length=300)),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to=config.utils.upload_path
                    ),
                ),
                (
                    "leader",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="team",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
