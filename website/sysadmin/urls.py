from django.urls import path

from . import views

app_name = "sysadmin"

urlpatterns = [
    path('', views.main, name = 'main'),
    path('main', views.main),
    path('volunteer/add', views.volunteer_add, name = 'volunteer_add'),
    path('volunteer/<slug:user_uuid>/remove', views.volunteer_remove, name = 'volunteer_remove'),
    path('email', views.EMailView.as_view(), name = 'email'),
]
