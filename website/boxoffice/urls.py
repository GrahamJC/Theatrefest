from django.urls import path

from . import views

app_name = "boxoffice"

urlpatterns = [
    path('', views.SelectView.as_view(), name = 'select'),
    path('home', views.HomeView.as_view(), name = 'home'),
    path('ajax/get_performances', views.get_performances, name = 'get_performances'),
    path('ajax/get_ticket_info', views.get_ticket_info, name = 'get_ticket_info'),
]
