# Generated by Django 5.0.2 on 2024-02-19 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_alter_product_variant_max_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product_variant',
            name='thumbnail_image',
            field=models.ImageField(upload_to='images/'),
        ),
    ]
