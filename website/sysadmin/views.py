from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View
from django.forms import formset_factory, modelformset_factory
from django.http import JsonResponse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from crispy_forms.bootstrap import FormActions, StrictButton

from accounts.models import User

from .forms import VolunteerForm, EMailForm


def _create_volunteer_form(postData = None):
    form = VolunteerForm(postData)
    helper = FormHelper()
    helper.form_tag = False
    helper.label_class = "col-xs-12 col-sm-3"
    helper.field_class= "col-xs-12, col-sm-9"
    form.helper = helper
    return form

def _render_volunteers(request, volunteer_form = None):
    context = {
        'volunteer_form': volunteer_form or _create_volunteer_form(),
        'volunteers': User.objects.filter(is_volunteer = True),
    }
    return render(request, 'sysadmin/_main_volunteers.html', context)

@user_passes_test(lambda u: u.is_admin)
@login_required
def main(request):
    volunteer_form = _create_volunteer_form()
    context = {
        'tab': 'volunteers',
        'volunteer_form': volunteer_form,
        'volunteers': User.objects.filter(is_volunteer = True).order_by('last_name', 'first_name'),
    }
    return render(request, 'sysadmin/main.html', context)


@user_passes_test(lambda u: u.is_admin)
def volunteer_add(request):
    form = _create_volunteer_form(request.POST)
    if form.is_valid():
        volunteer = form.cleaned_data['user']
        volunteer.first_name = form.cleaned_data['first_name']
        volunteer.last_name = form.cleaned_data['last_name']
        volunteer.is_volunteer = True
        volunteer.save()
        form = None
    return _render_volunteers(request, form)


@user_passes_test(lambda u: u.is_admin)
def volunteer_remove(request, user_uuid):
    volunteer = get_object_or_404(User, uuid = user_uuid)
    volunteer.is_volunteer = False
    volunteer.save()
    return _render_volunteers(request)


class EMailView(View):

    def get(self, request):
        form = EMailForm(initial={'from_email': settings.DEFAULT_FROM_EMAIL, 'to_email': 'graham.cockell@outlook.com', 'subject': 'Test', 'body': 'Hello world!'})
        return render(request, "sysadmin/email.html", { 'form': form })


    def post(self, request):
        form = EMailForm(request.POST)
        if form.is_valid():
            send_mail(form.cleaned_data['subject'], form.cleaned_data['body'], form.cleaned_data['from_email'], [form.cleaned_data['to_email']])
            form = EMailForm(initial={'from_email': settings.DEFAULT_FROM_EMAIL, 'to_email': 'graham.cockell@outlook.com', 'subject': 'Test', 'body': 'Hello world!'})
        return render(request, "sysadmin/email.html", { 'form': form })



