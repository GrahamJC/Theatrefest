from django.views import View
from django.shortcuts import render
from django.contrib.auth.views import LoginView as BaseLoginView

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from registration.backends.default.views import RegistrationView as BaseRegistrationView

class LoginView(BaseLoginView):

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['use_required_attribute'] = False
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        helper = FormHelper()
        helper.form_tag = False
        helper.label_class = "col-sm-2"
        helper.field_class = "col-sm-10"
        helper.add_input(Submit('submit', 'Login'))
        context['form_helper'] = helper
        return context


class RegistrationView(BaseRegistrationView):

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['use_required_attribute'] = False
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        helper = FormHelper()
        helper.form_tag = False
        helper.label_class = "col-sm-2"
        helper.field_class = "col-sm-10"
        helper.add_input(Submit('submit', 'Register'))
        context['form_helper'] = helper
        return context


class ProfileView(View):

    template_name = "accounts/profile.html"
    
    def get(self, request):
        return render(request, self.template_name, {})
        
    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, {})
        
