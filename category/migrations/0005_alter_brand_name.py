# Generated by Django 5.0.2 on 2024-02-16 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0004_brand_is_active_alter_brand_name_alter_brand_slug_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='name',
            field=models.CharField(max_length=15),
        ),
    ]
