# Generated by Django 5.0.2 on 2024-03-05 10:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("checkout", "0006_checkout"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="order_status",
            field=models.CharField(default="pending", max_length=15),
        ),
        migrations.AddField(
            model_name="order",
            name="payment_method",
            field=models.CharField(default="COD", max_length=15),
        ),
        migrations.AddField(
            model_name="order",
            name="payment_status",
            field=models.CharField(default="pending", max_length=15),
        ),
    ]
