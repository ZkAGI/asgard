# Generated by Django 4.2.4 on 2023-09-11 21:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("twitter", "0002_twitteraccount"),
    ]

    operations = [
        migrations.AddField(
            model_name="twitteraccount",
            name="oauth_token",
            field=models.CharField(default="hello", max_length=255),
            preserve_default=False,
        ),
    ]
