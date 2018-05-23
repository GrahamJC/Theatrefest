from django.urls import path

from . import views

app_name = "program"

urlpatterns = [
    path('', views.home, name = 'home'),
    path('show', views.ShowsView.as_view(), name = 'shows'),
    path('show/<int:show_id>', views.ShowDetailView.as_view(), name = 'show_detail'),
    path('schedule', views.ScheduleView.as_view(), name = 'schedule'),
    path('schedule_pdf', views.SchedulePdfView.as_view(), name = 'schedule_pdf'),
    path('venue', views.VenuesView.as_view(), name = 'venues'),
    path('venue/<int:venue_id>', views.VenueDetailView.as_view(), name = 'venue_detail'),
]
