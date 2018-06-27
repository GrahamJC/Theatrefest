from django.urls import path

from . import views
from . import apis

app_name = "boxoffice"

urlpatterns = [
    # Select
    path('select', views.select, name = 'select'),
    # Main page
    path('<slug:box_office_uuid>', views.main, name = 'main'),
    path('<slug:box_office_uuid>/tab/<str:tab>', views.main, name = 'main'),
    # Sale AJAX support
    path('<slug:box_office_uuid>/sale', views.sale_start, name = 'sale_start'),
    path('sale/show/<slug:show_uuid>/performances', views.sale_show_performances, name = 'sale_show_performances'),
    path('sale/<slug:sale_uuid>/add/tickets', views.sale_add_tickets, name = 'sale_add_tickets'),
    path('sale/<slug:sale_uuid>/update/extras', views.sale_update_extras, name = 'sale_update_extras'),
    path('sale/<slug:sale_uuid>/remove/performance/<slug:performance_uuid>', views.sale_remove_performance, name = 'sale_remove_performance'),
    path('sale/<slug:sale_uuid>/remove/ticket/<slug:ticket_uuid>', views.sale_remove_ticket, name = 'sale_remove_ticket'),
    path('sale/<slug:sale_uuid>/complete', views.sale_complete, name = 'sale_complete'),
    path('sale/<slug:sale_uuid>/cancel', views.sale_cancel, name = 'sale_cancel'),
    # Refund AJAX support
    path('<slug:box_office_uuid>/refund', views.refund_start, name = 'refund_start'),
    path('refund/<slug:refund_uuid>/add/ticket', views.refund_add_ticket, name = 'refund_add_ticket'),
    path('refund/<slug:refund_uuid>/remove/ticket/<slug:ticket_uuid>', views.refund_remove_ticket, name = 'refund_remove_ticket'),
    path('refund/<slug:refund_uuid>/complete', views.refund_complete, name = 'refund_complete'),
    path('refund/<slug:refund_uuid>/cancel', views.refund_cancel, name = 'refund_cancel'),
    # Admission AJAX support
    path('<slug:box_office_uuid>/admission/shows', views.admission_shows, name = 'admission_shows'),
    path('admission/show/<slug:show_uuid>/performances', views.admission_show_performances, name = 'admission_show_performances'),
    path('admission/performance/<slug:performance_uuid>/tickets', views.admission_performance_tickets, name = 'admission_performance_tickets'),
    # Report AJAX support
    path('<slug:box_office_uuid>/report/summary/<str:yyyymmdd>', views.report_summary, name = 'report_summary'),
    path('<slug:box_office_uuid>/report/sales/<str:yyyymmdd>', views.report_sales, name = 'report_sales'),
    path('sale/<slug:sale_uuid>/report', views.report_sale_detail, name = 'report_sale_detail'),
    path('<slug:box_office_uuid>/report/refunds<str:yyyymmdd>', views.report_refunds, name = 'report_refunds'),
    path('refund/<slug:refund_uuid>/report', views.report_refund_detail, name = 'report_refund_detail'),
]
