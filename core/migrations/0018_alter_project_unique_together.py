# Generated by Django 4.2.4 on 2023-10-16 06:04

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0017_alter_userprofile_tweets_left"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="project",
            unique_together={("user", "name")},
        ),
    ]
