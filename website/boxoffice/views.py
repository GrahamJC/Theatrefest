from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View
from django.forms import formset_factory, modelformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from crispy_forms.bootstrap import FormActions, StrictButton, FieldWithButtons

from tickets.models import BoxOffice

class HomeView(LoginRequiredMixin, View):

    def get(self,request):

        # Check to see if there is a box office selected
        try:
            boxoffice = BoxOffice.objects.get(pk = request.session.get('boxoffice_id', None))
        except BoxOffice.DoesNotExist:
            return redirect(reverse('boxoffice:select'))

        # Render box office home page
        context = {
            'boxoffice': boxoffice,
        }
        return render(request, 'boxoffice/home.html', context)


class SelectView(LoginRequiredMixin, View):

    def get(self,request):

        # Let user select a box office
        context = {
            'boxoffices': BoxOffice.objects.exclude(is_online = True),
        }
        return render(request, 'boxoffice/select.html', context)

    @transaction.atomic
    def post(self, request):

        # Save selected box office
        request.session['boxoffice_id'] = request.POST['boxoffice_id']

        # Go to box office home page
        return redirect(reverse('boxoffice:home'))

