# Generated by Django 5.0.2 on 2024-02-10 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_1', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customers',
            name='phone',
            field=models.IntegerField(blank=True),
        ),
    ]
