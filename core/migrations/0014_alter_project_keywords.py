# Generated by Django 4.2.4 on 2023-09-08 19:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0013_alter_project_keywords"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="keywords",
            field=models.JSONField(blank=True, null=True),
        ),
    ]