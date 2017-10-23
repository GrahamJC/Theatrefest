"""
URLconf for registration and activation, using django-registration's
default backend.

If the default behavior of these views is acceptable to you, simply
use a line like this in your root URLconf to set up the default URLs
for registration::

    (r'^accounts/', include('registration.backends.default.urls')),

This will also automatically set up the views in
``django.contrib.auth`` at sensible default locations.

If you'd like to customize registration behavior, feel free to set up
your own URL patterns for these views instead.

"""

from django.conf.urls import include
from django.conf.urls import url
from django.conf import settings
from django.views.generic.base import TemplateView

from registration.views import ActivationView
from registration.views import RegistrationView
from registration.views import ResendActivationView

from .views import ProfileView


urlpatterns = [
    # django-registration-redux
    url(r'^activate/complete/$',
        TemplateView.as_view(template_name='registration/activation_complete.html'),
        name='registration_activation_complete'),
    url(r'^activate/resend/$',
        ResendActivationView.as_view(),
        name='registration_resend_activation'),
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r'^activate/(?P<activation_key>\w+)/$',
        ActivationView.as_view(),
        name='registration_activate'),
    url(r'^register/complete/$',
        TemplateView.as_view(template_name='registration/registration_complete.html'),
        name='registration_complete'),
    url(r'^register/closed/$',
        TemplateView.as_view(template_name='registration/registration_closed.html'),
        name='registration_disallowed'),
    url(r'^register/$',
        RegistrationView.as_view(),
        name='registration_register'),
    # auth views
    url(r'', include('registration.auth_urls')),
    # Theatrefest additions
    url(r'^profile/$', ProfileView.as_view(), name='profile'),
]

# ===========================================================
#from django.conf.urls import url, include
#from django.views.generic.base import TemplateView
#from django.contrib.auth import views as auth_views

#from registration import views as reg_views

#from . import views
#from .forms import MyAuthenticationForm

#urlpatterns = [
#    url(r'^register/$', views.MyRegistrationView.as_view(), name='registration_register'),
#    url(r'^register/closed/$', TemplateView.as_view(template_name='registration/registration_closed.html'), name='registration_disallowed'),
#    url(r'^login/$', auth_views.LoginView.as_view(template_name='registration/login.html', authentication_form = MyAuthenticationForm), name='auth_login'),
#    url(r'^logout/$', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='auth_logout'),
#    url(r'^password/change/$', auth_views.PasswordChangeView.as_view(success_url='auth_password_change_done'), name='auth_password_change'),
#    url(r'^password/change/done/$', auth_views.PasswordChangeDoneView.as_view(), name='auth_password_change_done'),
#    url(r'^password/reset/$', auth_views.PasswordResetView.as_view(success_url='auth_password_reset_done'), name='auth_password_reset'),
#    url(r'^password/reset/complete/$', auth_views.PasswordResetCompleteView.as_view(), name='auth_password_reset_complete'),
#    url(r'^password/reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='auth_password_reset_done'),
#    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
#        auth_views.PasswordResetConfirmView.as_view(success_url='auth_password_reset_complete'),
#        name='auth_password_reset_confirm'),
#    url(r'^profile/$', views.ProfileView.as_view(), name='profile'),
#]

