# Generated by Django 4.1.2 on 2023-02-11 11:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_alter_promocode_end_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='promocode',
            old_name='start_time',
            new_name='valid_from',
        ),
        migrations.RemoveField(
            model_name='promocode',
            name='end_time',
        ),
        migrations.AddField(
            model_name='promocode',
            name='valid_to',
            field=models.DateTimeField(default=datetime.datetime(2023, 2, 18, 11, 23, 11, 500653, tzinfo=datetime.timezone.utc), verbose_name='Дата окончания'),
        ),
    ]
