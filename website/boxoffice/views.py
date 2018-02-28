from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View
from django.forms import formset_factory, modelformset_factory
from django.http import JsonResponse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from crispy_forms.bootstrap import FormActions, StrictButton, FieldWithButtons

from program.models import Show, Performance
from tickets.models import BoxOffice

from .forms import TicketsForm

class HomeView(LoginRequiredMixin, View):

    def get(self,request):

        # Check to see if there is a box office selected
        try:
            boxoffice = BoxOffice.objects.get(pk = request.session.get('boxoffice_id', None))
        except BoxOffice.DoesNotExist:
            return redirect(reverse('boxoffice:select'))

        # Render box office home page
        form = TicketsForm()
        context = {
            'boxoffice': boxoffice,
            'form': form,
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

# AJAX helpers
def get_performances(request):

    show = Show.objects.get(pk = request.GET.get('show_id', 0))
    performances = []
    for performance in show.performances.all():
        performances.append({
            "id": performance.id,
            "date": performance.date,
            "time": performance.time,
            "tickets_available": performance.tickets_available,
        })
    data = {
        "performances": performances,
    }
    return JsonResponse(data)

def get_ticket_info(request):

    performance = Performance.objects.get(pk = request.GET.get('performance_id', 0))
    data = {
        "capacity": performance.show.venue.capacity,
        "sold": performance.tickets_sold,
        "available": performance.tickets_available,
    }
    return JsonResponse(data)

