# Generated by Django 5.0.2 on 2024-02-19 07:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_product_variant_max_price_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='products',
            name='slug',
        ),
    ]