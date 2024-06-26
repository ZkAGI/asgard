# Generated by Django 4.2.4 on 2023-09-08 19:13

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0012_remove_project_website"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="keywords",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=350),
                blank=True,
                null=True,
                size=None,
            ),
        ),
    ]
