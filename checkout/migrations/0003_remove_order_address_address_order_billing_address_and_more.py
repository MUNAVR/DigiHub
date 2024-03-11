# Generated by Django 5.0.2 on 2024-03-04 19:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app_1", "0007_address2"),
        ("checkout", "0002_order_address"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="address",
        ),
        migrations.CreateModel(
            name="Address",
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
                ("first_name", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(max_length=15)),
                ("address", models.CharField(max_length=255)),
                ("locality", models.CharField(max_length=100)),
                ("state", models.CharField(max_length=100)),
                ("district", models.CharField(max_length=100)),
                ("pincode", models.CharField(max_length=10)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="app_1.customers",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="order",
            name="billing_address",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="billing_orders",
                to="checkout.address",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="delivery_address",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="delivery_orders",
                to="checkout.address",
            ),
        ),
    ]
