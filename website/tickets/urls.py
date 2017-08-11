from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^fringers$', views.FringersView.as_view(), name = 'fringers'),
    url(r'^buy/(?P<performance_id>[0-9]+)$', views.BuyView.as_view(), name = 'buy'),
    url(r'^basket$', views.BasketView.as_view(), name = 'basket'),
    url(r'^checkout$', views.CheckoutView.as_view(), name = 'checkout'),
]
