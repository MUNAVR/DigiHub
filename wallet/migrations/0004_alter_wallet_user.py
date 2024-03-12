# Generated by Django 5.0.2 on 2024-03-12 06:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app_1", "0007_address2"),
        ("wallet", "0003_rename_stutus_wallet_transaction"),
    ]

    operations = [
        migrations.AlterField(
            model_name="wallet",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="app_1.customers"
            ),
        ),
    ]