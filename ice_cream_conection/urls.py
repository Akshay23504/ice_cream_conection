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
    url(r'^truck/newDestination/$', views.new_destination, name='truck_new_destination'),
    # url(r'^dashboard/customer/$', views.CustomerDashboardView.as_view(), name='customer_dashboard'),
    # url(r'^dashboard/driver/$', views.DriverDashboardView.as_view(), name='driver_dashboard'),
]
