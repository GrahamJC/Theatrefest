from django.conf import settings
from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView

from registration.backends.default.views import ResendActivationView

from .views import LoginView, RegistrationView, ActivationView, PasswordResetView, ProfileView

app_name = "accounts"

urlpatterns = []
if settings.TRAINING:
    # django-registration-redux simple backend
    urlpatterns += [
        path('register/closed/', TemplateView.as_view(template_name = 'registration/registration_closed.html'), name = 'registration_disallowed'),
        path('register/', RegistrationView.as_view(success_url = reverse_lazy("program:shows")), name = 'registration_register'),
    ]
else:
    urlpatterns += [
        # django-registration-redux default backend
        path('activate/complete/', TemplateView.as_view(template_name = 'registration/activation_complete.html'), name = 'registration_activation_complete'),
        path('activate/resend/', ResendActivationView.as_view(), name = 'registration_resend_activation'),
        path('activate/<activation_key>/', ActivationView.as_view(), name = 'registration_activate'),
        path('register/complete/', TemplateView.as_view(template_name = 'registration/registration_complete.html'), name = 'registration_complete'),
        path('register/closed/', TemplateView.as_view(template_name = 'registration/registration_closed.html'), name = 'registration_disallowed'),
        path('register/', RegistrationView.as_view(success_url = reverse_lazy("accounts:registration_complete")), name = 'registration_register'),
    ]
urlpatterns += [
    # auth views
    path('login/', LoginView.as_view(template_name = 'registration/login.html'), name = 'auth_login'),
    path('logout/', auth_views.LogoutView.as_view(template_name = 'registration/logout.html'), name = 'auth_logout'),
    path('password/change/', auth_views.PasswordChangeView.as_view(success_url = reverse_lazy('accounts:auth_password_change_done')), name = 'auth_password_change'),
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(), name = 'auth_password_change_done'),
    path('password/reset/', PasswordResetView.as_view(success_url = reverse_lazy('accounts:auth_password_reset_done')), name = 'auth_password_reset'),
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name = 'auth_password_reset_complete'),
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(), name = 'auth_password_reset_done'),
    path('password/reset/confirm/<str:uidb64>/<str:token>/', auth_views.PasswordResetConfirmView.as_view(success_url = reverse_lazy('accounts:auth_password_reset_complete')), name = 'auth_password_reset_confirm'),
    # Theatrefest additions
    path('profile/', ProfileView.as_view(), name = 'profile'),
]
