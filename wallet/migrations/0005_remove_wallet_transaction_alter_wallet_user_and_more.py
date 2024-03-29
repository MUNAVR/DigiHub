# Generated by Django 5.0.2 on 2024-03-12 06:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app_1", "0007_address2"),
        ("wallet", "0004_alter_wallet_user"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="wallet",
            name="transaction",
        ),
        migrations.AlterField(
            model_name="wallet",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="app_1.customers"
            ),
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "transaction_type",
                    models.CharField(
                        choices=[("Credit", "Credit"), ("Debit", "Debit")],
                        max_length=10,
                    ),
                ),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                (
                    "wallet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="wallet.wallet"
                    ),
                ),
            ],
        ),
    ]
