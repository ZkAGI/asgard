# Generated by Django 4.2.4 on 2023-09-12 14:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("twitter", "0003_twitteraccount_oauth_token"),
    ]

    operations = [
        migrations.AddField(
            model_name="tweets",
            name="author_id",
            field=models.CharField(default="1234", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="tweets",
            name="tweet_id",
            field=models.CharField(default="4321", max_length=255),
            preserve_default=False,
        ),
    ]