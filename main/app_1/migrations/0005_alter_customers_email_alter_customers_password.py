# Generated by Django 5.0.2 on 2024-02-23 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_1', '0004_customers_is_blocked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customers',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='customers',
            name='password',
            field=models.CharField(blank=True, max_length=30, unique=True),
        ),
    ]
