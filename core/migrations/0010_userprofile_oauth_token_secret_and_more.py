# Generated by Django 4.2.4 on 2023-09-08 17:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0009_AcessTokeninUserProf"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="oauth_token_secret",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="twitter_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
