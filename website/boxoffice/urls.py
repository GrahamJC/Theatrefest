from django.urls import path

from . import views
from . import apis

app_name = "boxoffice"

urlpatterns = [
    # Select
    path('', views.select),
    path('select', views.select, name = 'select'),
    path('select/<int:box_office_id>', views.select, name = 'select'),
    # Main page
    path('main', views.main, name = 'main'),
    path('main/<str:tab>', views.main, name = 'main'),
    # Sale AJAX support
    path('sale/start', views.sale_start, name = 'sale_start'),
    path('sale/show/<int:show_id>/performances', views.sale_show_performances, name = 'sale_show_performances'),
    path('sale/add/tickets', views.sale_add_tickets, name = 'sale_add_tickets'),
    path('sale/update/extras', views.sale_update_extras, name = 'sale_update_extras'),
    path('sale/remove/performance/<int:performance_id>', views.sale_remove_performance, name = 'sale_remove_performance'),
    path('sale/remove/ticket/<int:ticket_id>', views.sale_remove_ticket, name = 'sale_remove_ticket'),
    path('sale/complete', views.sale_complete, name = 'sale_complete'),
    path('sale/cancel', views.sale_cancel, name = 'sale_cancel'),
    # Refund AJAX support
    path('refund/add/ticket', views.refund_add_ticket, name = 'refund_add_ticket'),
    path('refund/remove/ticket/<int:ticket_id>', views.refund_remove_ticket, name = 'refund_remove_ticket'),
    path('refund/complete', views.refund_complete, name = 'refund_complete'),
    path('refund/cancel', views.refund_cancel, name = 'refund_cancel'),
    path('refund/new', views.refund_new, name = 'refund_new'),
    # Admission AJAX support
    path('admission/shows', views.admission_shows, name = 'admission_shows'),
    path('admission/show/<int:show_id>/performances', views.admission_show_performances, name = 'admission_show_performances'),
    path('admission/performance/<int:performance_id>/tickets', views.admission_performance_tickets, name = 'admission_performance_tickets'),
    # Report AJAX support
    path('report/summary/<str:yyyymmdd>', views.report_summary, name = 'report_summary'),
    path('report/sales/<str:yyyymmdd>', views.report_sales, name = 'report_sales'),
    path('report/sale/<int:sale_id>', views.report_sale_detail, name = 'report_sale_detail'),
    path('report/refunds<str:yyyymmdd>', views.report_refunds, name = 'report_refunds'),
    path('report/refund/<int:refund_id>', views.report_refund_detail, name = 'report_refund_detail'),
]
