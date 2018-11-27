from django.conf.urls import url
from django.contrib import admin
from django.views.generic import RedirectView

from . import views

admin.autodiscover()

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/login/'), name='index'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^truck/updateCoordinate/$', views.truck_update_coordinate, name='truck_update_coordinate'),
    url(r'^customer/updateCoordinate/$', views.customer_update_coordinate, name='customer_update_coordinate'),
    url(r'^truck/newDestination/$', views.truck_new_destination, name='truck_new_destination'),
    url(r'^truck/getCustomers/$', views.truck_get_customers, name='truck_get_customers'),
    url(r'^customer/getTrucks/$', views.customer_get_trucks, name='customer_get_trucks'),
    url(r'^truck/sendCustomers/$', views.truck_send_customers, name='truck_send_customers'),
    url(r'^truck/reachedDestination/$', views.truck_reached_destination, name='truck_reached_destination'),
    url(r'^truck/getCustomerRequests/$', views.get_all_customers_for_truck, name='get_all_customers_for_truck'),
    url(r'^customers/all/$', views.get_all_customers, name='get_all_customers'),
    url(r'^trucks/all/$', views.get_all_trucks, name='get_all_trucks'),
    # url(r'^mapsPage/$', views.MapsPageView.as_view(), name='ui_page'),
    # url(r'^dashboard/customer/$', views.CustomerDashboardView.as_view(), name='customer_dashboard'),
    # url(r'^dashboard/driver/$', views.DriverDashboardView.as_view(), name='driver_dashboard'),
]
