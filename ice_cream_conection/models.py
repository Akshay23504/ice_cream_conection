import datetime
import enum
from django.contrib.auth.models import User
from django.db import models


class Role(enum.Enum):
    """
    An Enum for the roles - ice cream truck driver and customer

    """

    truck = 1
    customer = 2


class Profile(models.Model):
    """
    This model contains all the information about the users. An id is generated
    automatically by the database. The creation of the user record is also
    recorded in a separate column. The role which is an enum is stored in its
    own column. The served_by_id applies only for customers. It represents the
    id of the truck which is serving that particular customer.

    """

    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    role = models.CharField(max_length=100, default=Role.truck)
    created_time = models.DateTimeField(default=datetime.datetime.now())
    served_by_id = models.IntegerField(null=True)


class Coordinates(models.Model):
    """
    Coordinates table contains the information about the latest positions of
    both the customers and the ice cream truck drivers. The user_id field is a
    one-to-one relationship with the id column of the Profile table. That means,
    each user (customer or truck driver) will have exactly one entry in the
    Coordinates table. The latitude and longitude columns have the up-to-date
    coordinates for each user. The destination fields are only applicable to
    the truck driver. It will contain valid coordinates when the truck driver
    is moving from point A to point B. Point B coordinates is the destination
    and is stored in the destination fields. The destination fields go back to
    the default value of null when the truck reaches the destination.

    """

    user_id = models.OneToOneField(Profile, on_delete=models.CASCADE, primary_key=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    destination_latitude = models.FloatField(null=True)
    destination_longitude = models.FloatField(null=True)


class TruckCustomer(models.Model):
    """
    This table is a helper table which stores a mapping from truck to customers.
    It contains the entries for truck drivers and the customers for each truck
    driver that is being served or requested or were served. Note that there is
    also a valid field. This field is activated when the customer requests for
    a particular truck and the truck driver accepts it. So, this table can
    contain entries for a truck and all the customers for this truck. One truck
    many customers. When the truck reaches the destination, all the customers
    active for this truck are made inactive. This means that the truck has now
    served yummy ice creams to the customers. Mission complete!!!

    """

    truck_id = models.IntegerField(null=True)
    customer_id = models.IntegerField(null=True)
    valid = models.BooleanField(default=False, null=False)

