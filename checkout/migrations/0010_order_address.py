# Generated by Django 5.0.2 on 2024-03-20 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0009_order_delivery_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
