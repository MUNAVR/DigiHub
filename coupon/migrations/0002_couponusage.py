# Generated by Django 5.0.2 on 2024-03-18 15:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_1', '0007_address2'),
        ('coupon', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CouponUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_used', models.DateTimeField(auto_now_add=True)),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coupon.coupon')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_1.customers')),
            ],
            options={
                'unique_together': {('user', 'coupon')},
            },
        ),
    ]