from django.urls import path

from . import views

app_name = "program"

urlpatterns = [
    path('', views.home, name = 'home'),
    path('show', views.ShowsView.as_view(), name = 'shows'),
    path('show/<int:show_id>', views.show_detail, name = 'show_detail'),
    path('venue', views.venues, name = 'venues'),
    path('venue/<int:venue_id>', views.venue_detail, name = 'venue_detail'),
]
