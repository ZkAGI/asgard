# Generated by Django 4.2.4 on 2023-09-03 09:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_SoupTextinProject"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="url",
            field=models.URLField(default="https://polybase.xyz/"),
            preserve_default=False,
        ),
    ]
