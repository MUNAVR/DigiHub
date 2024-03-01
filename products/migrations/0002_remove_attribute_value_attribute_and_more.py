# Generated by Django 5.0.2 on 2024-02-16 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attribute_value',
            name='attribute',
        ),
        migrations.RenameField(
            model_name='attribute_value',
            old_name='attribute_value',
            new_name='attribute_color',
        ),
        migrations.AddField(
            model_name='attribute_value',
            name='attribute_ram',
            field=models.CharField(default=0, max_length=50, unique=True),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Attribute',
        ),
    ]
