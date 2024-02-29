# Generated by Django 5.0.2 on 2024-02-28 07:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_1', '0006_address1'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=30)),
                ('locality', models.CharField(max_length=20)),
                ('pincode', models.IntegerField()),
                ('district', models.CharField(max_length=14)),
                ('state', models.CharField(max_length=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_1.customers')),
            ],
        ),
    ]
