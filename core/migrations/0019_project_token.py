# Generated by Django 4.2.4 on 2023-10-26 16:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0018_alter_project_unique_together"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="token",
            field=models.TextField(blank=True, null=True),
        ),
    ]
