from django.conf.urls import url

from . import views

app_name = "catalog"

urlpatterns = [
    url(r'^$', views.home, name = 'home'),
    url(r'^show$', views.shows, name = 'shows'),
    url(r'^show/(?P<show_id>[0-9]+)$', views.show_detail, name = 'show_detail'),
    url(r'^venue$', views.venues, name = 'venues'),
    url(r'^venue/(?P<venue_id>[0-9]+)$', views.venue_detail, name = 'venue_detail'),
]
