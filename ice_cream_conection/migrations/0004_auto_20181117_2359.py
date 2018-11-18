# Generated by Django 2.1.1 on 2018-11-17 23:59

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ice_cream_conection', '0003_auto_20181013_0531'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coordinates',
            fields=[
                ('user_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='ice_cream_conection.Profile')),
                ('latitude', models.FloatField(null=True)),
                ('longitude', models.FloatField(null=True)),
                ('destination_latitude', models.FloatField(null=True)),
                ('destination_longitude', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TruckCustomer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('truck_id', models.IntegerField(null=True)),
                ('customer_id', models.IntegerField(null=True)),
                ('valid', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='profile',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 11, 17, 23, 59, 45, 437408)),
        ),
    ]
