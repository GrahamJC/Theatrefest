from django.urls import path, include
from django.views.generic.base import TemplateView

from registration.views import ActivationView
from registration.views import RegistrationView
from registration.views import ResendActivationView

from .views import ProfileView

urlpatterns = [
    # django-registration-redux
    path('activate/complete/', TemplateView.as_view(template_name='registration/activation_complete.html'), name='registration_activation_complete'),
    path('activate/resend/', ResendActivationView.as_view(), name='registration_resend_activation'),
    path('activate/<activation_key>/', ActivationView.as_view(), name='registration_activate'),
    path('register/complete/', TemplateView.as_view(template_name='registration/registration_complete.html'), name='registration_complete'),
    path('register/closed/', TemplateView.as_view(template_name='registration/registration_closed.html'), name='registration_disallowed'),
    path('register/', RegistrationView.as_view(), name='registration_register'),
    # auth views
    path('', include('registration.auth_urls')),
    # Theatrefest additions
    path('profile/', ProfileView.as_view(), name='profile'),
]
