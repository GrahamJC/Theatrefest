from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import RedirectView

import debug_toolbar

from registration import views

urlpatterns = [
    path('', RedirectView.as_view(url = '/program/show', permanent = True)),
    path('content/', include('content.urls')),
    path('program/', include('program.urls')),
    path('accounts/', include('accounts.urls')),
    path('tickets/', include('tickets.urls')),
    path('boxoffice/', include('boxoffice.urls')),
    path('reports/', include('reports.urls')),
    path('sysadmin/', include('sysadmin.urls')),
    path('admin/', admin.site.urls),
    path('debug/', include(debug_toolbar.urls)),
]

# Serve static and media files
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

