# Generated by Django 5.0.2 on 2024-03-09 13:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("offers", "0003_remove_referraloffer_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="brandoffer",
            name="valid_from",
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="productoffer",
            name="valid_from",
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="referraloffer",
            name="valid_from",
            field=models.DateField(auto_now_add=True),
        ),
    ]
