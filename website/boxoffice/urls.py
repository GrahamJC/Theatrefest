from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.SelectView.as_view(), name = 'select'),
    url(r'^/home$', views.HomeView.as_view(), name = 'home'),
]
