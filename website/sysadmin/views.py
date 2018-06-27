from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce, Lower
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
from program.models import Show, Performance
from tickets.models import Sale, Ticket, Fringer

from .forms import VolunteerForm, SaleSearchForm, SaleEditForm, EMailForm

# Logging
import logging
logger = logging.getLogger(__name__)

# Helpers
def _create_volunteer_form(post_data = None):
    form = VolunteerForm(post_data)
    helper = FormHelper()
    helper.form_tag = False
    helper.label_class = "col-xs-3"
    helper.field_class= "col-xs-9"
    form.helper = helper
    return form

def _render_volunteers(request, volunteer_form = None):
    context = {
        'volunteer_form': volunteer_form or _create_volunteer_form(),
        'volunteers': User.objects.filter(is_volunteer = True),
    }
    return render(request, 'sysadmin/_main_volunteers.html', context)

def _create_sale_search_form(sale = None, post_data = None):
    initial_data = []
    if sale:
        initial_data = { 'sale_id': sale.id }
    form = SaleSearchForm(post_data, initial = initial_data)
    helper = FormHelper()
    helper.form_tag = False
    helper.label_class = "col-xs-3"
    helper.field_class= "col-xs-9"
    form.helper = helper
    return form

def _create_sale_edit_form(sale = None, post_data = None):
    initial_data = []
    if sale:
        initial_data = { 'buttons': sale.buttons, 'fringers': sale.fringers.count() }
    form = SaleEditForm(post_data, initial = initial_data)
    helper = FormHelper()
    helper.form_tag = False
    helper.label_class = "col-xs-3"
    helper.field_class= "col-xs-9"
    form.helper = helper
    return form

def _render_sales(request, sale, search_form = None, edit_form = None):
    context = {
        'sale': sale,
        'sale_search_form': search_form or _create_sale_search_form(sale),
        'sale_edit_form': edit_form or _create_sale_edit_form(sale),
    }
    return render(request, 'sysadmin/_main_sales.html', context)
 
@user_passes_test(lambda u: u.is_admin)
@login_required
def main(request):

    # Voulnteers
    volunteer_form = _create_volunteer_form()

    # Ticket sales
    shows = []
    for show in Show.objects.filter(venue__is_ticketed = True).order_by(Lower('name')):
        performances = []
        for performance in show.performances.all():
            tickets = Ticket.objects.filter(performance = performance, sale__completed__isnull = False, refund__isnull = True)
            performances.append({
                'date': performance.date,
                'time': performance.time,
                'tickets': tickets.count(),
                'cost': tickets.aggregate(sum_cost = Coalesce(Sum('cost'), 0))['sum_cost'],
            })
        tickets = Ticket.objects.filter(performance__show = show, sale__completed__isnull = False, refund__isnull = True)
        shows.append({
            'name': show.name,
            'tickets': tickets.count(),
            'cost': tickets.aggregate(sum_cost = Coalesce(Sum('cost'), 0))['sum_cost'],
            'performances': performances,
        })

    # Render main page
    context = {
        'tab': 'volunteers',
        'volunteer_form': volunteer_form,
        'volunteers': User.objects.filter(is_volunteer = True).order_by('last_name', 'first_name'),
        'shows': shows,
        'sale': None,
        'sale_search_form': _create_sale_search_form(),
        'sale_edit_form': _create_sale_edit_form(),
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


# Sales
@user_passes_test(lambda u: u.is_admin)
def sale_search(request):
    sale = None
    form = _create_sale_search_form(None, request.POST)
    if form.is_valid():
        try:
            sale = Sale.objects.get(pk = form.cleaned_data['sale_id'])
            if not sale.completed:
                form.add_error('sale_id', 'Sale not completed')
                sale = None
            elif not sale.box_office:
                form.add_error('sale_id', 'Online sale')
                sale = None
            else:
                form = None
        except Sale.DoesNotExist:
            form.add_error('sale_id', 'Sale not found')
    return _render_sales(request, sale, search_form = form)

@user_passes_test(lambda u: u.is_admin)
def sale_clear(request):
    return _render_sales(request, None)

@user_passes_test(lambda u: u.is_admin)
def sale_update(request, sale_uuid):
    sale = get_object_or_404(Sale, uuid = sale_uuid)
    form = None
    if not sale.completed:
        logger.error('sale_update: incomplete sale %s', sale)
        sale = None
    elif not sale.box_office:
        logger.error('sale_update: online sale %s', sale)
        sale = None
    else:
        form = _create_sale_edit_form(sale, request.POST)
        if form.is_valid():
            sale.buttons = form.cleaned_data['buttons']
            fringers = form.cleaned_data['fringers']
            while (sale.fringers.count() or 0) > fringers:
                sale.fringers.first().delete()
            while (sale.fringers.count() or 0) < fringers:
                fringer = Fringer(
                    description = '6 shows for £18',
                    shows = 6,
                    cost = 18,
                    sale = sale,
                )
                fringer.save()
            sale.amount = sale.total_cost
            sale.save()
            logger.info("Sale %s extras updated: %d buttons, %d fringers", sale, sale.buttons, sale.fringers.count())
            form = None
    return _render_sales(request, sale, edit_form = form)

@user_passes_test(lambda u: u.is_admin)
def sale_ticket_remove(request, sale_uuid, ticket_uuid):
    sale = get_object_or_404(Sale, uuid = sale_uuid)
    if not sale.completed:
        logger.error('sale_ticket_remove: incomplete sale %s', sale)
        sale = None
    elif not sale.box_office:
        logger.error('sale_ticket_remove: online sale %s', sale)
        sale = None
    else:
        ticket = get_object_or_404(Ticket, uuid = ticket_uuid)
        if ticket.sale != sale:
            logger.error('sale_ticket_remove: ticket %s not part of sale %s', ticket, sale)
        else:
            ticket.delete()
            sale.amount = sale.total_cost
            sale.save()
    return _render_sales(request, sale)

@user_passes_test(lambda u: u.is_admin)
def sale_delete(request, sale_uuid):
    sale = get_object_or_404(Sale, uuid = sale_uuid)
    if not sale.completed:
        logger.error('sale_delete: incomplete sale %s', sale)
        sale = None
    elif not sale.box_office:
        logger.error('sale_delete: online sale %s', sale)
        sale = None
    else:
        sale.delete()
        sale = None
    return _render_sales(request, sale)

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



