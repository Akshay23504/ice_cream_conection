import json
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from urllib.parse import unquote

from ice_cream_conection.models import Profile, Role, Coordinates


class LoginView(TemplateView):
    template_name = 'login.html'


# class CustomerDashboardView(TemplateView):
#     template_name = 'customer_dashboard.html'


# class DriverDashboardView(TemplateView):
#     template_name = 'driver_dashboard.html'


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
            profile.role = Role.driver
        else:
            profile.role = Role.customer
        profile.save()
        coordinates = Coordinates()
        coordinates.user_id = profile
        coordinates.save()
    else:
        result = Profile.objects.filter(email=details['email'])
        if driver:
            if result[0].role != str(Role.driver):
                response = HttpResponseRedirect("/login/")
                response.set_cookie("icc_invalid_role", "User email and role do not match")
                return response
        else:
            if result[0].role != str(Role.customer):
                response = HttpResponseRedirect("/login/")
                response.set_cookie("icc_invalid_role", "User email and role do not match")
                return response

    if driver:
        response = HttpResponseRedirect("http://localhost:4200")
        response.set_cookie("icc_driver_login", details['first_name'] + " " + details['last_name'])
        return response
    else:
        response = HttpResponseRedirect("http://localhost:4200")
        response.set_cookie("icc_customer_login", details['first_name'] + " " + details['last_name'])
        return response


@csrf_exempt
def truck_update_coordinate(request):
    if request.method == "POST":
        body = json.loads(request.body)
        print(body)
        print(body["user_id"])
        return JsonResponse({"success": "true"})
    else:
        return HttpResponse(status=405)


@csrf_exempt
def customer_update_coordinate(request):
    if request.method == "POST":
        body = json.loads(request.body)
        print(body)
        print(body["user_id"])
        return JsonResponse({"success": "true"})
    else:
        return HttpResponse(status=405)