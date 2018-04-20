from django.urls import path

from . import views
from . import apis

app_name = "boxoffice"

urlpatterns = [
    path('', views.SelectView.as_view(), name = 'select'),
    path('sale', views.SaleView.as_view(), name = 'sale'),
    path('sale/remove/performance/<int:performance_id>', views.sale_remove_performance, name = 'sale_remove_performance'),
    path('sale/remove/ticket/<int:ticket_id>', views.sale_remove_ticket, name = 'sale_remove_ticket'),
    path('sale/print/<int:sale_id>', views.SalePrintView.as_view(), name = 'sale_print'),
    # AJAX helpers
    path('api/get_performances', apis.get_performances, name = 'api_get_performances'),
]
