import datetime
import enum
from django.contrib.auth.models import User
from django.db import models


class Role(enum.Enum):
    driver = 1
    customer = 2


class Profile(models.Model):
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    role = models.CharField(max_length=100, default=Role.driver)
    created_time = models.DateTimeField(default=datetime.datetime.now())
