from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    # Sales
    path('sale/<slug:sale_uuid>/pdf', views.sale_pdf, name = 'sale_pdf'),
    # Refunds
    path('refund/<slug:refund_uuid>/pdf', views.refund_pdf, name = 'refund_pdf'),
    # Admissions
    path('admission/<slug:performance_uuid>/pdf', views.admission_pdf, name = 'admission_pdf'),
]
