from django.urls import path

from . import views

app_name = "tickets"

urlpatterns = [
    path('myaccount', views.MyAccountView.as_view(), name = 'myaccount'),
    path('myaccount/confirm/fringers', views.MyAccountConfirmFringersView.as_view(), name = 'myaccount_confirm_fringers'),
    path('buy/<int:performance_id>', views.BuyView.as_view(), name = 'buy'),
    path('buy/confirm/tickets/<int:performance_id>', views.BuyConfirmTicketsView.as_view(), name = 'buy_confirm_tickets'),
    path('buy/confirm/fringer_tickets/<int:performance_id>', views.BuyConfirmFringerTicketsView.as_view(), name = 'buy_confirm_fringer_tickets'),
    path('buy/confirm/fringers/<int:performance_id>', views.BuyConfirmFringersView.as_view(), name = 'buy_confirm_fringers'),
    path('checkout', views.CheckoutView.as_view(), name = 'checkout'),
    path('checkout/remove/performance/<int:performance_id>', views.CheckoutRemovePerformanceView.as_view(), name = 'checkout_remove_performance'),
    path('checkout/remove/ticket/<int:ticket_id>', views.CheckoutRemoveTicketView.as_view(), name = 'checkout_remove_ticket'),
    path('checkout/remove/fringer/<int:fringer_id>', views.CheckoutRemoveFringerView.as_view(), name = 'checkout_remove_fringer'),
    path('checkout/confirm/<int:sale_id>', views.CheckoutConfirmView.as_view(), name = 'checkout_confirm'),
    path('cancel/ticket/<int:ticket_id>', views.CancelTicketView.as_view(), name = 'cancel_ticket'),
    path('buy/<str:theatrefest_id>/<str:yyyymmdd>/<str:hhmm>', views.TheatrefestBuyView.as_view(), name = 'theatrefest_buy'),
    path('print/sale/<int:sale_id>', views.PrintSaleView.as_view(), name = 'print_sale'),
    path('print/performance/<int:performance_id>', views.PrintPerformanceView.as_view(), name = 'print_performance'),
]
