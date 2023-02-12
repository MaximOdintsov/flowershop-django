# Generated by Django 4.1.2 on 2023-02-11 12:47

import datetime
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_rename_start_time_promocode_valid_from_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='promocode',
            name='is_valid',
            field=models.BooleanField(default=True, verbose_name='Действителен'),
        ),
        migrations.AlterField(
            model_name='promocode',
            name='valid_from',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Действует с'),
        ),
        migrations.AlterField(
            model_name='promocode',
            name='valid_to',
            field=models.DateTimeField(default=datetime.datetime(2023, 2, 18, 12, 47, 37, 895589, tzinfo=datetime.timezone.utc), verbose_name='Действует до'),
        ),
    ]
