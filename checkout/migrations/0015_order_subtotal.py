# Generated by Django 5.0.2 on 2024-03-21 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0014_checkout_cart_items'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]