# Generated by Django 4.2.4 on 2023-09-01 20:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_TweetsModel"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="ai_rules",
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="project",
            name="keywords",
            field=models.TextField(null=True),
        ),
    ]
