# Generated by Django 4.2.4 on 2023-12-29 10:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("listner", "0002_tgverifiedusers"),
    ]

    operations = [
        migrations.CreateModel(
            name="Quest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("title", models.CharField(max_length=100)),
                ("description", models.CharField(max_length=250)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
