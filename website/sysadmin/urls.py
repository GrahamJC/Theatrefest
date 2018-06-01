from django.urls import path

from . import views

app_name = "sysadmin"

urlpatterns = [
    path('email', views.EMailView.as_view(), name = 'email'),
]
