# Generated by Django 5.0 on 2024-01-08 07:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_team_activity_types_team_personality_type_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="team",
            name="activity_types",
        ),
    ]