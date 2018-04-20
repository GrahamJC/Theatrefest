from django.urls import path

from . import views

app_name = "tickets"

urlpatterns = [
    path('fringers', views.FringersView.as_view(), name = 'fringers'),
    path('show', views.ShowView.as_view(), name = 'show'),
    path('buy/<int:performance_id>', views.BuyView.as_view(), name = 'buy'),
    path('buy/<str:theatrefest_id>/<str:yyyymmdd>/<str:hhmm>', views.TheatrefestBuyView.as_view(), name = 'theatrefest_buy'),
    path('checkout', views.CheckoutView.as_view(), name = 'checkout'),
    path('remove/fringer/<int:fringer_id>', views.RemoveFringerView.as_view(), name = 'remove_fringer'),
    path('remove/performance/<int:performance_id>', views.RemovePerformanceView.as_view(), name = 'remove_performance'),
    path('remove/ticket/<int:ticket_id>', views.RemoveTicketView.as_view(), name = 'remove_ticket'),
    path('cancel/ticket/<int:ticket_id>', views.CancelTicketView.as_view(), name = 'cancel_ticket'),
    path('print/ticket/<int:ticket_id>', views.PrintTicketView.as_view(), name = 'print_ticket'),
]
