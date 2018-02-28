from django.urls import path

from . import views
from . import apis

app_name = "boxoffice"

urlpatterns = [
    path('', views.SelectView.as_view(), name = 'select'),
    path('home', views.HomeView.as_view(), name = 'home'),
    # AJAX helpers
    path('api/get_performances', apis.get_performances, name = 'api_get_performances'),
    path('api/get_ticket_info', apis.get_ticket_info, name = 'api_get_ticket_info'),
]
