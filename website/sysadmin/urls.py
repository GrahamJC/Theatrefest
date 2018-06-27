from django.urls import path

from . import views

app_name = "sysadmin"

urlpatterns = [
    path('', views.main, name = 'main'),
    path('main', views.main),
    path('volunteer/add', views.volunteer_add, name = 'volunteer_add'),
    path('volunteer/<slug:user_uuid>/remove', views.volunteer_remove, name = 'volunteer_remove'),
    path('sale/search', views.sale_search, name = 'sale_search'),
    path('sale/clear', views.sale_clear, name = 'sale_clear'),
    path('sale/<slug:sale_uuid>/update', views.sale_update, name = 'sale_update'),
    path('sale/<slug:sale_uuid>/remove/<slug:ticket_uuid>', views.sale_ticket_remove, name = 'sale_ticket_remove'),
    path('sale/<slug:sale_uuid>/delete', views.sale_delete, name = 'sale_delete'),
    path('email', views.EMailView.as_view(), name = 'email'),
]
