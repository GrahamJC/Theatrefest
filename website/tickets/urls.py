from django.conf.urls import url

from . import views

app_name = "tickets"

urlpatterns = [
    url(r'^fringers$', views.FringersView.as_view(), name = 'fringers'),
    url(r'^show$', views.ShowView.as_view(), name = 'show'),
    url(r'^buy/(?P<performance_id>[0-9]+)$', views.BuyView.as_view(), name = 'buy'),
    url(r'^checkout$', views.CheckoutView.as_view(), name = 'checkout'),
    url(r'^remove/fringer/(?P<fringer_id>[0-9]+)$', views.RemoveFringerView.as_view(), name = 'remove_fringer'),
    url(r'^remove/ticket/(?P<ticket_id>[0-9]+)$', views.RemoveTicketView.as_view(), name = 'remove_ticket'),
    url(r'^cancel/ticket/(?P<ticket_id>[0-9]+)$', views.CancelTicketView.as_view(), name = 'cancel_ticket'),
    url(r'^print/ticket/(?P<ticket_id>[0-9]+)$', views.PrintTicketView.as_view(), name = 'print_ticket'),
]
