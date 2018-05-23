from django.views import View
from django.shortcuts import render
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import PasswordResetView as BasePasswordResetView
from django.urls import reverse, reverse_lazy

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Hidden, Submit

from registration.backends.default.views import RegistrationView as BaseRegistrationView
from registration.backends.default.views import ActivationView as BaseActivationView
#from registration.backends.simple.views import RegistrationView as BaseRegistrationView

class LoginView(BaseLoginView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        helper = FormHelper()
        helper.form_class = "form-horizontal"
        helper.form_action = reverse("accounts:auth_login")
        helper.label_class = "col-sm-3"
        helper.field_class = "col-sm-9"
        helper.add_input(Submit('submit', 'Login'))
        helper.add_input(Hidden('next', context['next']))
        context['form_helper'] = helper
        return context


class RegistrationView(BaseRegistrationView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        helper = FormHelper()
        helper.form_class = "form-horizontal"
        helper.form_action = reverse("accounts:registration_register")
        helper.label_class = "col-sm-3"
        helper.field_class = "col-sm-9"
        helper.add_input(Submit('submit', 'Register'))
        context['form_helper'] = helper
        return context


class PasswordResetView(BasePasswordResetView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        helper = FormHelper()
        helper.form_class = "form-horizontal"
        helper.form_action = reverse("accounts:auth_password_reset")
        helper.label_class = "col-sm-3"
        helper.field_class = "col-sm-9"
        helper.add_input(Submit('submit', 'Reset'))
        context['form_helper'] = helper
        return context

class ActivationView(BaseActivationView):

    def get_success_url(self, user):
        return ('accounts:registration_activation_complete', (), {})


class ProfileView(View):

    template_name = "accounts/profile.html"
    
    def get(self, request):
        return render(request, self.template_name, {})
        
    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, {})
        
