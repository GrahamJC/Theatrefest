from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import RedirectView

from registration import views

urlpatterns = [
    path('', RedirectView.as_view(url = '/program/', permanent = True)),
    path('program/', include('program.urls')),
    path('accounts/', include('accounts.urls')),
    #path('accounts/', include('registration.backends.default.urls')),
    path('tickets/', include('tickets.urls')),
    path('boxoffice/', include('boxoffice.urls')),
    path('admin/', admin.site.urls),
]

# Serve static files
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

