from django.conf.urls import url
from django.contrib import admin

from . import views

admin.autodiscover()

urlpatterns = [
    url(r'^$', views.HomePageView.as_view(), name='index'),
    url(r'^home/$', views.HomePageView.as_view(), name='home'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^profile/$', views.update_profile),
    url(r'^account/logout/$', views.logout),
]
