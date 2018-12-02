from math import radians, sin, cos, asin, sqrt

import datetime
import json
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from urllib.parse import unquote

from ice_cream_conection.models import Profile, Role, Coordinates, TruckCustomer


class LoginView(TemplateView):
    """
    The HTML file template for the login page is served from here.

    """

    template_name = 'login.html'

# The below three views are commented out as it is not in use now.
# The customer and driver dashboards are taken by a separate Angular app and
# hence not needed here.
# The maps page is just a filler for the UI because it wasn't ready and is still
# in progress!!

# class CustomerDashboardView(TemplateView):
#     template_name = 'customer_dashboard.html'


# class DriverDashboardView(TemplateView):
#     template_name = 'driver_dashboard.html'


# class MapsPageView(TemplateView):
#     template_name = 'maps_page.html'


def get_user_details(backend, strategy, details, response, request, user=None, *args, **kwargs):
    """
    Before the description of this beautiful method, there is a question that
    needs some answers - Where is this method being called from?
    Answer: I do not know. It's a mystery. PyCharm wasn't able to find it's
    root also. My guess is, the social-django app calls this method and is
    in-built. But, hey...this works...and that's all it matters.

    This method is being called by someone and the control of the code comes
    here after successful authentication of login. So, the control works like
    this:
    1. The user goes to the beautiful login page
    2. Django serves the login page
    3. The client (browser of course) renders the login page
    4. The user selects the role and accepts the terms
    5. Clicks on "Sign In with Google"
    6. The URL redirects to Google webpages
    7. User selects their account. If there is only one Google account, Google
    automatically chooses it. Might need permissions for the first time.
    8. Now upon successful authentication, Google redirects back to the home
    page. The home page is configured in the Google Developer Console.
    9. Google will just tell if it is a successful authentication or not and if
    it is successful, then it redirects to home page (which is login page). Now,
    how do I know what is the user email, which role did the user select? This
    is where this life-saving method kicks-in!

    I don't know how, but before Google redirects back to the home page, the
    control comes to this method. If it were redirecting to the home page and I
    hadn't written this method, (more like discovered), then the login would
    have become cumbersome. And the best part about this method, it has a ton
    of parameters which contains every detail that is required.

    So, now the further steps are:
    10. Control comes to this method before redirecting
    11. Everything required for the app is present in the parameters. Use them
    and create profiles. If it is an existing user, then verify.
    12. Then, instead of redirecting to home page, redirect to the dashboard
    of the particular user
    13. Sweet...!

    All the above steps pretty much sums up what this method is doing.

    :param backend: Not in use
    :param strategy: Not in use
    :param details: Details of the Google user in JSON format
    :param response: Since it is redirection from this method, response is not
    in use
    :param request: The in-depth details of the request. Can be used to set
    and get cookies
    :param user: Not in use
    :param args: Not in use
    :param kwargs: Not in use

    """

    # By the default the user is not a driver
    driver = False
    """
    Use "icc_role_selected" to check if the cookie exists. If the cookie 
    exists, then it is an existing user. Check the value of the cookie. The
    "icc_role_selected" cookie tells us the role of the user - driver or
    customer.
    
    """
    if "icc_role_selected" in request.COOKIES:
        if "driver" in unquote(request.COOKIES.get('icc_role_selected')):
            driver = True

    # If there is no email in the database, then it is a new customer.
    if Profile.objects.filter(email=details['email']).count() == 0:
        # Create a new profile object
        profile = Profile()
        # Add the details of the user from the "details" JSON
        profile.first_name = details['first_name']
        profile.last_name = details['last_name']
        profile.email = details['email']
        # Choose the role based on the driver variable which is set previously
        if driver:
            profile.role = Role.truck
        else:
            profile.role = Role.customer
        # Save the profile to the database
        profile.save()
        """
        Since the Coordinates table is a one-to-one mapping of the Profile
        table, it is ideal to create an entry in this table here. 
        
        """
        # Create a new coordinates object
        coordinates = Coordinates()
        # Foreign key mapping
        coordinates.user_id = profile
        # Save the coordinates object to the database
        coordinates.save()
        # Needed for future
        user_id = profile.id
    else:
        # This is for existing customers
        result = Profile.objects.filter(email=details['email'])
        print(result[0])
        # Needed for future
        user_id = result[0].id
        """
        Just make sure no one has tampered with the role and the request
        for log in is a valid existing customer with the proper role
        If the role received from the request and the role in the database do
        not match for a user, then redirect them back to login page. 
        
        """
        if driver:
            print("In driver")
            if result[0].role != str(Role.truck):
                print(result[0].role)
                print(str(Role.truck))
                print(result[0].role != str(Role.truck))
                # Very less probability of coming here
                response = HttpResponseRedirect("/login/")
                response.set_cookie("icc_invalid_role", "User email and role do not match")
                return response
        else:
            print("In customer")
            if result[0].role != str(Role.customer):
                print(result[0].role)
                print(str(Role.truck))
                print(result[0].role != str(Role.truck))
                # Very less probability of coming here
                response = HttpResponseRedirect("/login/")
                response.set_cookie("icc_invalid_role", "User email and role do not match")
                return response

    if driver:
        # Redirect the driver to truck dashboard with some GET parameter set
        # response = HttpResponseRedirect("http://localhost:4200")
        # response = HttpResponseRedirect("/mapsPage/")
        response = HttpResponseRedirect("https://ice-cream-conection-ui.herokuapp.com/truck/dashboard?userId=" +
                                        str(user_id))
        response.set_cookie("icc_driver_login", details['first_name'] + " " + details['last_name'])
        # Finally, return the response from this mystery method
        return response
    else:
        # Redirect the user to the customer dashboard with some GET parameter set
        # response = HttpResponseRedirect("http://localhost:4200")
        response = HttpResponseRedirect("https://ice-cream-conection-ui.herokuapp.com/customer/dashboard?userId=" +
                                        str(user_id))
        response.set_cookie("icc_customer_login", details['first_name'] + " " + details['last_name'])
        # Finally, return the response from this mystery method
        return response


def haversine(latitude_1, longitude_1, latitude_2, longitude_2):
    """
    Haversine is the formula that is used to calculate the distance between
    two points on the globe like geometrical object. The radius of the
    geometrical object (earth) is required for the calculation. The calculation
    is pretty simple and is explained below with a radius threshold of 2.5
    kilometers.

    If the method is called in scope of getting all customers near a truck,
    then the truck coordinates will be latitude_1 and longitude_1. The customer
    coordinates will be latitude_2 and longitude_2. The truck coordinates remain
    constant with several different customer coordinates. Imagine as, the truck
    coordinate is at the center of the circle and the customer coordinates are
    checked if it lies within the boundary of the circle.

    If the method is called in scope of getting all trucks near a customer,
    then the customer coordinates will be latitude_1 and longitude_1. The truck
    coordinates will be latitude_2 and longitude_2. The customer coordinates
    remain constant with several different truck coordinates. Imagine as, the
    customer coordinate is at the center of the circle and the truck
    coordinates are checked if it lies within the boundary of the circle.

    :param latitude_1: Latitude of the customer or truck
    :param longitude_1: Longitude of the customer or truck
    :param latitude_2: Latitude of the customer or truck
    :param longitude_2: Longitude of the customer or truck
    :return: Return true or false if the customer and the truck are within the
    radius or vicinity.

    """

    radius = 2.5  # In Kilometer
    # Degree to radians
    latitude_1, longitude_1, latitude_2, longitude_2 = \
        map(radians, [latitude_1, longitude_1, latitude_2, longitude_2])

    # Haversine formula
    d_latitude = latitude_2 - latitude_1
    d_longitude = longitude_2 - longitude_1
    a = sin(d_latitude / 2) ** 2 + cos(latitude_1) * cos(latitude_2) * sin(d_longitude / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r <= radius


@csrf_exempt
def truck_update_coordinate(request):
    """
    This simple method updates the coordinates of the truck in the Coordinate
    table. The request will contain the truck id and the coordinates to update
    in JSON format. The request is of the POST type.

    :param request: Truck id, latitude and longitude of the truck
    :return: 405 if the request is not POST
    Otherwise, return the same request body.

    """

    # Check if the request type if POST
    if request.method == "POST":
        # Deserialize the JSON because it will be in bytes
        body = json.loads(request.body)
        # Make success true
        body["success"] = True
        result = Coordinates.objects.filter(user_id=body['truck_id'])
        if not result.exists() or result[0].user_id.role != str(Role.truck):
            # Make success false if something goes wrong
            body["success"] = False
            # Return the body JSON
            return JsonResponse(body)
        # The result variable is immutable. So, put it to a new coordinates
        # object
        coordinates = result[0]
        coordinates.latitude = body["latitude"]
        coordinates.longitude = body["longitude"]
        # Save the coordinates object
        coordinates.save()

        # Return the body JSON
        return JsonResponse(body)
    else:
        # Return method not allowed
        return HttpResponse(status=405)


@csrf_exempt
def customer_update_coordinate(request):
    """
    This simple method updates the coordinates of the customer in the
    Coordinate table. The request will contain the customer id and the
    coordinates to update in JSON format. The request is of the POST type.

    :param request: Customer id, latitude and longitude of the customer
    :return: 405 if the request is not POST
    Otherwise, return the same request body.

    """

    # Check if the request type if POST
    if request.method == "POST":
        # Deserialize the JSON because it will be in bytes
        body = json.loads(request.body)
        # Make success true
        body["success"] = True
        result = Coordinates.objects.filter(user_id=body['customer_id'])
        if not result.exists() or result[0].user_id.role != str(Role.customer):
            # Make success false if something goes wrong
            body["success"] = False
            # Return the body JSON
            return JsonResponse(body)
        # The result variable is immutable. So, put it to a new coordinates
        # object
        coordinates = result[0]
        coordinates.latitude = body["latitude"]
        coordinates.longitude = body["longitude"]
        # Save the coordinates object
        coordinates.save()

        # Return the body JSON
        return JsonResponse(body)
    else:
        # Return method not allowed
        return HttpResponse(status=405)


@csrf_exempt
def truck_new_destination(request):
    """
    This simple method updates the destination coordinates of the truck in the
    Coordinate table. The request will contain the truck id and the
    coordinates to update in JSON format. The request is of the POST type.

    :param request: Truck id, destination latitude and longitude of the truck
    :return: 405 if the request is not POST
    Otherwise, return the same request body.

    """

    # Check if the request type if POST
    if request.method == "POST":
        # Deserialize the JSON because it will be in bytes
        body = json.loads(request.body)
        # Make success true
        body["success"] = True
        result = Coordinates.objects.filter(user_id=body['truck_id'])
        if not result.exists() or result[0].user_id.role != str(Role.truck):
            # Make success false if something goes wrong
            body["success"] = False
            # Return the body JSON
            return JsonResponse(body)
        # The result variable is immutable. So, put it to a new coordinates
        # object
        coordinates = result[0]
        coordinates.destination_latitude = body["latitude"]
        coordinates.destination_longitude = body["longitude"]
        # Save the coordinates object
        coordinates.save()

        # Return the body JSON
        return JsonResponse(body)
    else:
        # Return method not allowed
        return HttpResponse(status=405)


@csrf_exempt
def truck_get_customers(request):
    """
    This method starts by first extracting the latitude and longitude from the
    request. These coordinates are the latest coordinates of the truck. Then,
    these coordinates are updated in the Coordinate table.

    After updating, all customer data from the Coordinate table are pulled.
    Since, the Coordinate and Profile table are mapped, joins are used to get
    all the customers from the Coordinate table. Then, each customer is checked
    using haversine if the customer is within the specified radius of the truck.
    All the customers within the boundary are added to the response.

    The request will contain the truck id, latitude and longitude in JSON
    format. The request is of the POST type.

    :param request: Truck id, latest latitude and longitude of the truck
    :return: 405 if the request is not POST
    Otherwise, return all the customers within the truck's vicinity

    """

    # Check if the request type if POST
    if request.method == "POST":
        # Deserialize the JSON because it will be in bytes
        body = json.loads(request.body)
        # Make success true
        body["success"] = True

        # First update the truck with its coordinates
        result = Coordinates.objects.filter(user_id=body['truck_id'])
        if not result.exists() or result[0].user_id.role != str(Role.truck):
            # Make success false if something goes wrong
            body["success"] = False
            # Return the body JSON
            return JsonResponse(body)
        # The result variable is immutable. So, put it to a new coordinates
        # object
        coordinates = result[0]
        coordinates.latitude = truck_latitude = body["latitude"]
        coordinates.longitude = truck_longitude = body["longitude"]
        # Save the coordinates object
        coordinates.save()

        # Get all customers within a radius
        result = Coordinates.objects.filter(user_id__role=str(Role.customer)).values()
        result = [entry for entry in result]  # Convert queryset to list
        body["customers"] = []
        for i in range(len(result)):
            if haversine(truck_latitude, truck_longitude, result[i]['latitude'], result[i]['longitude']):
                # Filter the customers
                body["customers"].append(result[i])

        # Return the body JSON
        return JsonResponse(body)
    else:
        # Return method not allowed
        return HttpResponse(status=405)


@csrf_exempt
def customer_get_trucks(request):
    """
    This method starts by first extracting the latitude and longitude from the
    request. These coordinates are the latest coordinates of the customer. Then,
    these coordinates are updated in the Coordinate table.

    After updating, all truck data from the Coordinate table are pulled.
    Since, the Coordinate and Profile table are mapped, joins are used to get
    all the trucks from the Coordinate table. Then, each truck is checked
    using haversine if the truck is within the specified radius of the customer.
    All the trucks within the boundary are added to the response.

    The request will contain the customer id, latitude and longitude in JSON
    format. The request is of the POST type.

    :param request: Customer id, latest latitude and longitude of the customer
    :return: 405 if the request is not POST
    Otherwise, return all the trucks within the customer's vicinity

    """

    # Check if the request type if POST
    if request.method == "POST":
        # Deserialize the JSON because it will be in bytes
        body = json.loads(request.body)
        # Make success true
        body["success"] = True

        # First update the customer with their coordinates
        result = Coordinates.objects.filter(user_id=body['customer_id'])
        if not result.exists() or result[0].user_id.role != str(Role.customer):
            # Make success false if something goes wrong
            body["success"] = False
            # Return the body JSON
            return JsonResponse(body)
        # The result variable is immutable. So, put it to a new coordinates
        # object
        coordinates = result[0]
        coordinates.latitude = customer_latitude = body["latitude"]
        coordinates.longitude = customer_longitude = body["longitude"]
        # Save the coordinates object
        coordinates.save()

        # Get all trucks within a radius
        result = Coordinates.objects.filter(user_id__role=str(Role.truck)).values()
        result = [entry for entry in result]  # Convert queryset to list
        body["trucks"] = []
        for i in range(len(result)):
            if haversine(customer_latitude, customer_longitude, result[i]['latitude'], result[i]['longitude']):
                # Filter the trucks
                body["trucks"].append(result[i])

        # Return the body JSON
        return JsonResponse(body)
    else:
        # Return method not allowed
        return HttpResponse(status=405)


@csrf_exempt
def truck_send_customers(request):
    """
    The method starts with deactivating all the previous customers served by
    the truck. Then, a one-to-many mapping is created between a truck and
    multiple customers. Note that a literal one-to-many mapping is not
    possible because truck_id and customer_id in the TruckCustomer table
    need to map to the same Profile table and is not possible. But, the
    TruckCustomer table will have a truck and multiple customers for each
    truck.

    The request will contain the truck id and all the customers requested this
    truck in an array in JSON format. The request is of the POST type.

    :param request: Truck id and list of customers to be served the truck
    :return: 405 if the request is not POST
    Otherwise, return the request body with success as true

    """

    # Check if the request type if POST
    if request.method == "POST":
        # Deserialize the JSON because it will be in bytes
        body = json.loads(request.body)
        # Make success true
        body["success"] = True

        # First make all entries for this truck id false
        TruckCustomer.objects.filter(truck_id=body["truck_id"], valid=True).update(valid=False)

        # Next add the customers who will be served by the truck and update served by entries
        for i in range(len(body["customers"])):
            # I know I know, I can do this in a batch...
            truck_customer = TruckCustomer()
            truck_customer.truck_id = body["truck_id"]
            truck_customer.customer_id = body["customers"][i]
            truck_customer.valid = True
            # Save the truck_customer object
            truck_customer.save()

            result = Profile.objects.filter(id=body["customers"][i])
            # The result variable is immutable. So, put it to a new profile
            # object
            profile = result[0]
            # Also update this field in the Profile table. So that, we know
            # this customer is being served by the truck. We can get this
            # information from the TruckCustomer table also, but ehhhh....
            profile.served_by_id = body["truck_id"]
            # This is not needed if the customer signs up. But for mocking, we create entries directly.
            if profile.created_time is None:
                profile.created_time = datetime.datetime.now()
            # Save the profile object
            profile.save()

        # Return the body JSON
        return JsonResponse(body)
    else:
        # Return method not allowed
        return HttpResponse(status=405)


@csrf_exempt
def truck_reached_destination(request):
    """
    This API is called when the truck reaches the destination. (as the name
    suggests...duhh). Some book-keeping stuff is done when the truck reaches
    the destination

    The request will contain the truck id in JSON format. The request is of
    the POST type.

    :param request: Just the truck id
    :return: 405 if the request is not POST
    Otherwise, return the request body with success as true

    """

    # Check if the request type if POST
    if request.method == "POST":
        # Deserialize the JSON because it will be in bytes
        body = json.loads(request.body)
        # Make success true
        body["success"] = True

        # Make all entries for this truck id false, because the truck reached destination and delicious ice cream
        # is being served. So, mission complete.
        TruckCustomer.objects.filter(truck_id=body["truck_id"], valid=True).update(valid=False)

        # Also make destination coordinates null. I don't think this is needed at all, but ehhh...just 1 line of code
        Coordinates.objects.filter(user_id=body["truck_id"]).update(
            destination_latitude=None, destination_longitude=None)

        # Get all customers who was/is being served by the truck
        result = Profile.objects.filter(served_by_id=body["truck_id"])
        for r in result:
            # The r variable is immutable. So, put it to a new profile
            # object
            profile = r
            # Make the served_by_id field None. Why? Because the ice cream has been served by the truck for this
            # customer and served_by_id is no longer valid.
            profile.served_by_id = None
            # This is not needed if the customer signs up. But for mocking, we create entries directly.
            if profile.created_time is None:
                profile.created_time = datetime.datetime.now()
            # Save the profile object
            profile.save()

        # Return the body JSON
        return JsonResponse(body)
    else:
        # Return method not allowed
        return HttpResponse(status=405)


@csrf_exempt
def get_all_customers(request):
    """
    This API responds with all the customers in JSON format with all the
    details of the customers.

    The request contains an empty body and is of the POST type.

    :param request: Actually nothing in the body
    :return: 405 if the request is not POST
    Otherwise, return the request body with success as true and all the
    customers

    """

    # Check if the request type if POST
    if request.method == "POST":
        # Make success true
        body = {"success": True}

        result = Profile.objects.filter(role=str(Role.customer)).values()
        result = [entry for entry in result]  # Convert queryset to list
        body["customers"] = result

        # Return the body JSON
        return JsonResponse(body)
    else:
        # Return method not allowed
        return HttpResponse(status=405)


@csrf_exempt
def get_all_trucks(request):
    """
    This API responds with all the trucks in JSON format with all the
    details of the trucks.

    The request contains an empty body and is of the POST type.

    :param request: Actually nothing in the body
    :return: 405 if the request is not POST
    Otherwise, return the request body with success as true and all the trucks

    """

    # Check if the request type if POST
    if request.method == "POST":
        # Make success true
        body = {"success": True}

        result = Profile.objects.filter(role=str(Role.truck)).values()
        result = [entry for entry in result]  # Convert queryset to list
        body["trucks"] = result

        # Return the body JSON
        return JsonResponse(body)
    else:
        # Return method not allowed
        return HttpResponse(status=405)


@csrf_exempt
def get_all_customers_for_truck(request):
    """
    This API responds with all the customers for a particular truck in JSON
    format. The list of customers contain only the customer ids and are
    currently requested for a truck and are waiting for the truck to serve
    delicious ice creams.

    The request contains truck_id and is of the POST type.

    :param request: Truck id of the customers
    :return: 405 if the request is not POST
    Otherwise, return the request body with success as true amd all the
    customers for a truck

    """

    # Check if the request type if POST
    if request.method == "POST":
        # Deserialize the JSON because it will be in bytes
        body = json.loads(request.body)
        # Make success true
        body["success"] = True
        body["customers"] = []

        result = TruckCustomer.objects.filter(truck_id=body["truck_id"], valid=True)
        for r in result:
            # Append all the customer ids to an array in the body
            body["customers"].append(r.customer_id)

        # Return the body JSON
        return JsonResponse(body)
    else:
        # Return method not allowed
        return HttpResponse(status=405)
