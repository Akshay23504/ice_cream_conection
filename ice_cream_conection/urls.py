from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'/', views.HomePageView.as_view(), name='home'),
    url(r'/', views.HomePageView1.as_view(), name='home1'),
]
