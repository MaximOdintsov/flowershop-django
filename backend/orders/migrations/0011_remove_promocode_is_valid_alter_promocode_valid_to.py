# Generated by Django 4.1.2 on 2023-02-11 12:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_promocode_is_valid_alter_promocode_valid_from_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promocode',
            name='is_valid',
        ),
        migrations.AlterField(
            model_name='promocode',
            name='valid_to',
            field=models.DateTimeField(default=datetime.datetime(2023, 2, 18, 12, 53, 36, 421321, tzinfo=datetime.timezone.utc), verbose_name='Действует до'),
        ),
    ]
