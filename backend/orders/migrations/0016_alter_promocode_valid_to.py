# Generated by Django 4.1.2 on 2023-03-01 19:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0015_rename_name_promocode_code_alter_promocode_valid_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promocode',
            name='valid_to',
            field=models.DateTimeField(default=datetime.datetime(2023, 3, 8, 19, 6, 1, 150748, tzinfo=datetime.timezone.utc), verbose_name='Действует до'),
        ),
    ]
