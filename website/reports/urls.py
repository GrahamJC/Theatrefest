from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    # Sales
    path('sale/<int:sale_id>/pdf', views.sale_pdf, name = 'sale_pdf'),
    # Refunds
    path('refund/<int:refund_id>/pdf', views.refund_pdf, name = 'refund_pdf'),
]
