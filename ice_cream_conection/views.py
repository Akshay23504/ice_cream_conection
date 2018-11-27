from math import radians, sin, cos, asin, sqrt

import json
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from urllib.parse import unquote

from ice_cream_conection.models import Profile, Role, Coordinates, TruckCustomer


class LoginView(TemplateView):
    template_name = 'login.html'


# class CustomerDashboardView(TemplateView):
#     template_name = 'customer_dashboard.html'


# class DriverDashboardView(TemplateView):
#     template_name = 'driver_dashboard.html'


# class MapsPageView(TemplateView):
#     template_name = 'maps_page.html'


# TODO: Comment
def get_user_details(backend, strategy, details, response, request, user=None, *args, **kwargs):
    driver = False
    if "icc_role_selected" in request.COOKIES:
        if "driver" in unquote(request.COOKIES.get('icc_role_selected')):
            driver = True

    if Profile.objects.filter(email=details['email']).count() == 0:
        profile = Profile()
        profile.first_name = details['first_name']
        profile.last_name = details['last_name']
        profile.email = details['email']
        if driver:
            profile.role = Role.truck
        else:
            profile.role = Role.customer
        profile.save()
        coordinates = Coordinates()
        coordinates.user_id = profile
        coordinates.save()
    else:
        result = Profile.objects.filter(email=details['email'])
        if driver:
            if result[0].role != str(Role.truck):
                response = HttpResponseRedirect("/login/")
                response.set_cookie("icc_invalid_role", "User email and role do not match")
                return response
        else:
            if result[0].role != str(Role.customer):
                response = HttpResponseRedirect("/login/")
                response.set_cookie("icc_invalid_role", "User email and role do not match")
                return response

    if driver:
        # response = HttpResponseRedirect("http://localhost:4200")
        # response = HttpResponseRedirect("/mapsPage/")
        response = HttpResponseRedirect("https://ice-cream-conection-ui.herokuapp.com/")
        response.set_cookie("icc_driver_login", details['first_name'] + " " + details['last_name'])
        return response
    else:
        # response = HttpResponseRedirect("http://localhost:4200")
        response = HttpResponseRedirect("https://ice-cream-conection-ui.herokuapp.com/")
        response.set_cookie("icc_customer_login", details['first_name'] + " " + details['last_name'])
        return response


def haversine(truck_latitude, truck_longitude, customer_latitude, customer_longitude):
    radius = 2.5  # In Kilometer
    # Degree to radians
    truck_latitude, truck_longitude, customer_latitude, customer_longitude = \
        map(radians, [truck_latitude, truck_longitude, customer_latitude, customer_longitude])

    # Haversine formula
    d_latitude = customer_latitude - truck_latitude
    d_longitude = customer_longitude - truck_longitude
    a = sin(d_latitude / 2) ** 2 + cos(truck_latitude) * cos(customer_latitude) * sin(d_longitude / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r <= radius


@csrf_exempt
def truck_update_coordinate(request):
    if request.method == "POST":
        body = json.loads(request.body)
        body["success"] = True
        result = Coordinates.objects.filter(user_id=body['truck_id'])
        if not result.exists() or result[0].user_id.role != str(Role.truck):
            body["success"] = False
            return JsonResponse(body)
        coordinates = result[0]
        coordinates.latitude = body["latitude"]
        coordinates.longitude = body["longitude"]
        coordinates.save()
        return JsonResponse(body)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def customer_update_coordinate(request):
    if request.method == "POST":
        body = json.loads(request.body)
        body["success"] = True
        result = Coordinates.objects.filter(user_id=body['customer_id'])
        if not result.exists() or result[0].user_id.role != str(Role.customer):
            body["success"] = False
            return JsonResponse(body)
        coordinates = result[0]
        coordinates.latitude = body["latitude"]
        coordinates.longitude = body["longitude"]
        coordinates.save()
        return JsonResponse(body)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def truck_new_destination(request):
    if request.method == "POST":
        body = json.loads(request.body)
        body["success"] = True
        result = Coordinates.objects.filter(user_id=body['truck_id'])
        if not result.exists() or result[0].user_id.role != str(Role.truck):
            body["success"] = False
            return JsonResponse(body)
        coordinates = result[0]
        coordinates.destination_latitude = body["latitude"]
        coordinates.destination_longitude = body["longitude"]
        coordinates.save()
        return JsonResponse(body)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def truck_get_customers(request):
    if request.method == "POST":
        body = json.loads(request.body)
        body["success"] = True

        # First update the truck with its coordinates
        result = Coordinates.objects.filter(user_id=body['truck_id'])
        if not result.exists() or result[0].user_id.role != str(Role.truck):
            body["success"] = False
            return JsonResponse(body)
        coordinates = result[0]
        coordinates.latitude = truck_latitude = body["latitude"]
        coordinates.longitude = truck_longitude = body["longitude"]
        coordinates.save()

        # Get all customers within a radius
        result = Coordinates.objects.filter(user_id__role=str(Role.customer)).values()
        result = [entry for entry in result]  # Convert queryset to list
        body["customers"] = []
        for i in range(len(result)):
            if haversine(truck_latitude, truck_longitude, result[i]['latitude'], result[i]['longitude']):
                body["customers"].append(result[i])
        return JsonResponse(body)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def customer_get_trucks(request):
    if request.method == "POST":
        body = json.loads(request.body)
        body["success"] = True

        # First update the customer with their coordinates
        result = Coordinates.objects.filter(user_id=body['customer_id'])
        if not result.exists() or result[0].user_id.role != str(Role.customer):
            body["success"] = False
            return JsonResponse(body)
        coordinates = result[0]
        coordinates.latitude = customer_latitude = body["latitude"]
        coordinates.longitude = customer_longitude = body["longitude"]
        coordinates.save()

        # Get all trucks within a radius
        result = Coordinates.objects.filter(user_id__role=str(Role.truck)).values()
        result = [entry for entry in result]  # Convert queryset to list
        body["trucks"] = []
        for i in range(len(result)):
            if haversine(customer_latitude, customer_longitude, result[i]['latitude'], result[i]['longitude']):
                body["trucks"].append(result[i])
        return JsonResponse(body)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def truck_send_customers(request):
    if request.method == "POST":
        body = json.loads(request.body)
        body["success"] = True

        # First make all entries for this truck id false
        TruckCustomer.objects.filter(truck_id=body["truck_id"], valid=True).update(valid=False)

        # Next add the customers who will be served by the truck
        for i in range(len(body["customers"])):
            # I know I know, I can do this in a batch...
            truck_customer = TruckCustomer()
            truck_customer.truck_id = body["truck_id"]
            truck_customer.customer_id = body["customers"][i]
            truck_customer.valid = True
            truck_customer.save()

        return JsonResponse(body)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def truck_reached_destination(request):
    if request.method == "POST":
        body = json.loads(request.body)
        body["success"] = True

        # Make all entries for this truck id false, because the truck reached destination and delicious ice cream
        # is being served. So, mission complete.
        TruckCustomer.objects.filter(truck_id=body["truck_id"], valid=True).update(valid=False)

        # Also make destination coordinates null. I don't think this is needed at all, but ehhh...just 1 line of code
        Coordinates.objects.filter(user_id=body["truck_id"]).update(
            destination_latitude=None, destination_longitude=None)

        return JsonResponse(body)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def get_all_customers(request):
    if request.method == "POST":
        body = json.loads(request.body)
        body["success"] = True

        result = Profile.objects.filter(role=str(Role.customer)).values()
        result = [entry for entry in result]  # Convert queryset to list
        body["customers"] = result

        return JsonResponse(body)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def get_all_trucks(request):
    if request.method == "POST":
        body = json.loads(request.body)
        body["success"] = True

        result = Profile.objects.filter(role=str(Role.truck)).values()
        result = [entry for entry in result]  # Convert queryset to list
        body["customers"] = result

        return JsonResponse(body)
    else:
        return HttpResponse(status=405)


