# Generated by Django 5.0.2 on 2024-03-04 14:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("checkout", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="address",
            field=models.CharField(default="Unknown", max_length=50),
        ),
    ]
