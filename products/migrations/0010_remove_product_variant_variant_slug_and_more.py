# Generated by Django 5.0.2 on 2024-02-19 10:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_product_variant_variant_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product_variant',
            name='variant_slug',
        ),
        migrations.RemoveField(
            model_name='products',
            name='product_slug',
        ),
    ]
