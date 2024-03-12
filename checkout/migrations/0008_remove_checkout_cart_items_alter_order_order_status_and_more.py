# Generated by Django 5.0.2 on 2024-03-05 13:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("checkout", "0007_order_order_status_order_payment_method_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="checkout",
            name="cart_items",
        ),
        migrations.AlterField(
            model_name="order",
            name="order_status",
            field=models.CharField(default="Pending", max_length=15),
        ),
        migrations.AlterField(
            model_name="order",
            name="payment_status",
            field=models.CharField(default="Pending", max_length=15),
        ),
    ]