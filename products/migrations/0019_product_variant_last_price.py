# Generated by Django 5.0.2 on 2024-03-13 06:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0018_product_variant_rom"),
    ]

    operations = [
        migrations.AddField(
            model_name="product_variant",
            name="last_price",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
    ]
