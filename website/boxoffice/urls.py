from django.conf.urls import url

from . import views

app_name = "boxoffice"

urlpatterns = [
    url(r'^$', views.SelectView.as_view(), name = 'select'),
    url(r'^home$', views.HomeView.as_view(), name = 'home'),
    url(r'^ajax/get_performances$', views.get_performances, name = 'get_performances'),
    url(r'^ajax/get_ticket_info$', views.get_ticket_info, name = 'get_ticket_info'),
]
