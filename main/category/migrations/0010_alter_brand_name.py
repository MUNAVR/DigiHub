# Generated by Django 5.0.2 on 2024-02-23 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0009_alter_brand_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='name',
            field=models.CharField(max_length=15),
        ),
    ]