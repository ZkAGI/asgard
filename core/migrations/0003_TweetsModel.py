# Generated by Django 4.2.4 on 2023-09-01 20:01

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_initialModelCreation"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Tweets",
        ),
    ]
