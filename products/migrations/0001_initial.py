# Generated by Django 5.0.2 on 2024-02-16 12:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('category', '0005_alter_brand_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribute_name', models.CharField(max_length=50, unique=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Attribute_Value',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribute_value', models.CharField(max_length=50, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.attribute')),
            ],
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product_description', models.TextField(max_length=250)),
                ('product_brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='category.brand')),
                ('product_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='category.category')),
            ],
        ),
        migrations.CreateModel(
            name='Product_Variant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('sale_price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('stock', models.IntegerField()),
                ('product_variant_slug', models.SlugField(blank=True, max_length=200, unique=True)),
                ('thumbnail_image', models.ImageField(upload_to='product_variant/images/')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('attributes', models.ManyToManyField(related_name='attributes', to='products.attribute_value')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.products')),
            ],
        ),
    ]