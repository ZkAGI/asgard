# Generated by Django 4.2.4 on 2023-09-03 09:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_UserProfileModel"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="soup_text",
            field=models.TextField(blank=True, null=True),
        ),
    ]