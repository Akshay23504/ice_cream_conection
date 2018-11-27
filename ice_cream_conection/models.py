import datetime
import enum
from django.contrib.auth.models import User
from django.db import models


class Role(enum.Enum):
    truck = 1
    customer = 2


class Profile(models.Model):
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    role = models.CharField(max_length=100, default=Role.truck)
    created_time = models.DateTimeField(default=datetime.datetime.now())
    served_by_id = models.IntegerField(null=True)


class Coordinates(models.Model):
    user_id = models.OneToOneField(Profile, on_delete=models.CASCADE, primary_key=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    destination_latitude = models.FloatField(null=True)
    destination_longitude = models.FloatField(null=True)


class TruckCustomer(models.Model):
    truck_id = models.IntegerField(null=True)
    customer_id = models.IntegerField(null=True)
    valid = models.BooleanField(default=False, null=False)

