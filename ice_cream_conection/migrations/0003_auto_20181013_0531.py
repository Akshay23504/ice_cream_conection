# Generated by Django 2.1.1 on 2018-10-13 05:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ice_cream_conection', '0002_auto_20181013_0528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 10, 13, 5, 31, 29, 212137)),
        ),
    ]
