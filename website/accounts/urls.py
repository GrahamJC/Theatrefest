from django.conf.urls import url, include
from django.views.generic.base import TemplateView
from django.contrib.auth import views as auth_views

from registration import views as reg_views

from . import views
from .forms import MyAuthenticationForm

urlpatterns = [
    url(r'^register/$', views.MyRegistrationView.as_view(), name='registration_register'),
    url(r'^register/closed/$', TemplateView.as_view(template_name='registration/registration_closed.html'), name='registration_disallowed'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='registration/login.html', authentication_form = MyAuthenticationForm), name='auth_login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='auth_logout'),
    url(r'^password/change/$', auth_views.PasswordChangeView.as_view(success_url='auth_password_change_done'), name='auth_password_change'),
    url(r'^password/change/done/$', auth_views.PasswordChangeDoneView.as_view(), name='auth_password_change_done'),
    url(r'^password/reset/$', auth_views.PasswordResetView.as_view(success_url='auth_password_reset_done'), name='auth_password_reset'),
    url(r'^password/reset/complete/$', auth_views.PasswordResetCompleteView.as_view(), name='auth_password_reset_complete'),
    url(r'^password/reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='auth_password_reset_done'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(success_url='auth_password_reset_complete'),
        name='auth_password_reset_confirm'),
    url(r'^profile/$', views.ProfileView.as_view(), name='profile'),
]

