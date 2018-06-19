import datetime
from decimal import Decimal

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

import arrow

from program.models import Show, Performance
from tickets.models import BoxOffice, Sale, Refund, TicketType, Ticket, Fringer

from .forms import SaleTicketsForm, SaleTicketSubForm, SaleExtrasForm, SaleForm, RefundTicketForm, RefundForm

# Logging
import logging
logger = logging.getLogger(__name__)

# Helpers
def _get_box_office(request):
    return get_object_or_404(BoxOffice, pk =  request.session.get('box_office_id', None))

def _get_sale(request):
    try:
        sale = Sale.objects.get(pk = request.session.get('sale_id', None))
    except Sale.DoesNotExist:
        sale = None
        request.session['sale_id'] = None
    return sale

def _create_sale(request):
    sale = Sale(
        box_office = _get_box_office(request),
        user = request.user
    )
    sale.save()
    request.session['sale_id'] = sale.id
    return sale

def _create_sale_tickets_form(post_data = None):
    # Create form and add crispy helper
    form = SaleTicketsForm(post_data)
    helper = FormHelper()
    helper.form_tag = False
    helper.label_class = "col-xs-12 col-sm-3"
    helper.field_class= "col-xs-12, col-sm-9"
    form.helper = helper
    return form

def _create_sale_ticket_subforms(post_data = None):
    # Build and populate ticket formset
    TicketFormset = formset_factory(SaleTicketSubForm, extra = 0)
    initial_data = [{'type_id': t.id, 'name': t.name, 'price': t.price, 'quantity': 0} for t in TicketType.objects.filter(is_admin = False)]
    return TicketFormset(post_data, initial=initial_data)

def _create_sale_extras_form(sale, post_data = None):
    # Create form and add crispy helper
    if post_data:
        form = SaleExtrasForm(post_data)
    else:
        data = {
            'buttons': sale.buttons if sale else 0,
            'fringers': sale.fringers.count() if sale else 0,
        }
        form = SaleExtrasForm(initial = data)
    helper = FormHelper()
    helper.form_tag = False
    helper.label_class = "col-xs-12 col-sm-3"
    helper.field_class= "col-xs-12, col-sm-9"
    form.helper = helper
    return form

def _create_sale_form(sale, post_data = None):
    # Create form and add crispy helper
    if post_data:
        form = SaleForm(post_data)
    else:
        data = {
            'amount': sale.total_cost if sale else 0,
        }
        form = SaleForm(initial = data)
    helper = FormHelper()
    helper.form_tag = False
    helper.label_class = "col-xs-12 col-sm-3"
    helper.field_class= "col-xs-12, col-sm-9"
    form.helper = helper
    return form

def _render_sale(request, sale_tickets_form = None, sale_ticket_subforms = None, sale_extras_form = None, sale_form = None):
    sale = _get_sale(request)
    context = {
        'sale_tickets_form': sale_tickets_form or _create_sale_tickets_form(),
        'sale_ticket_subforms': sale_ticket_subforms or _create_sale_ticket_subforms(),
        'sale_extras_form': sale_extras_form or _create_sale_extras_form(sale),
        'sale_form': sale_form or _create_sale_form(sale),
        'sale': sale,
    }
    return render(request, "boxoffice/_main_sale.html", context)

def _get_refund(request):
    try:
        refund = Refund.objects.get(pk = request.session.get('refund_id', None))
    except Refund.DoesNotExist:
        refund = None
        request.session['refund_id'] = None
    return refund

def _create_refund(request):
    refund = Refund(
        box_office = _get_box_office(request),
        user = request.user
    )
    refund.save()
    request.session['refund_id'] = refund.id
    return refund

def _create_refund_ticket_form(post_data = None):
    # Create form and add crispy helper
    form = RefundTicketForm(post_data)
    helper = FormHelper()
    helper.form_tag = False
    helper.label_class = "col-xs-12 col-sm-3"
    helper.field_class= "col-xs-12, col-sm-9"
    form.helper = helper
    return form

def _create_refund_form(refund, post_data = None):
    # Create form and add crispy helper
    if post_data:
        form = RefundForm(post_data)
    else:
        data = {
            'amount': refund.total_cost if refund else 0,
        }
        form = RefundForm(initial = data)
    form.fields['reason'].widget.attrs['rows'] = 4
    helper = FormHelper()
    helper.form_tag = False
    helper.label_class = "col-xs-12 col-sm-3"
    helper.field_class= "col-xs-12, col-sm-9"
    form.helper = helper
    return form

def _render_refund(request, refund_ticket_form = None, refund_form = None):
    refund = _get_refund(request)
    context = {
        'refund_ticket_form': refund_ticket_form or _create_refund_ticket_form(),
        'refund_form': refund_form or _create_refund_form(refund),
        'refund': refund,
    }
    return render(request, "boxoffice/_main_refund.html", context)
    
# View functions
@user_passes_test(lambda u: u.is_volunteer or u.is_admin)
@login_required
def select(request, box_office_id = None):
    # If a box office is specified select it, cancel any incomplete sales/refunds
    # and go to the main box office page
    if box_office_id:
        request.session['box_office_id'] = box_office_id
        for sale in request.user.sales.filter(completed__isnull = True):
            sale.delete();
        request.session['sale_id'] = None
        for refund in request.user.refunds.filter(completed__isnull = True):
            refund.delete();
        request.session['refund_id'] = None
        return redirect(reverse('boxoffice:main'))

    # Allow user to select box office
    request.session['box_office_id'] = None
    context = {
        'box_offices': BoxOffice.objects.all(),
    }
    return render(request, 'boxoffice/select.html', context)
    
@user_passes_test(lambda u: u.is_volunteer or u.is_admin)
@login_required
def main(request, tab = 'sale'):

    # Get the current box office
    box_office = _get_box_office(request)
    if not box_office:
        return redirect(reverse('boxoffice:select'))

    # Create forms and render box office page
    sale = _get_sale(request)
    refund = _get_refund(request)
    today = datetime.datetime.today()
    report_dates = [today - datetime.timedelta(days = n) for n in range(1, 14)]
    context = {
        'box_office': box_office,
        'tab': tab,
        'sale_tickets_form': _create_sale_tickets_form(),
        'sale_ticket_subforms': _create_sale_ticket_subforms(),
        'sale_extras_form': _create_sale_extras_form(sale),
        'sale_form': _create_sale_form(sale),
        'sale': sale,
        'refund_ticket_form': _create_refund_ticket_form(),
        'refund_form': _create_refund_form(refund),
        'refund' : refund,
        'report_today': f'{today:%Y%m%d}',
        'report_dates': [{ 'value': f'{d:%Y%m%d}', 'text': f'{d:%a, %b %d}'} for d in report_dates],
    }
    return render(request, 'boxoffice/main.html', context)

# AJAX sale support
def sale_show_performances(request, show_id):

    show = get_object_or_404(Show, pk = show_id)
    html = '<option value="0">-- Select performance --</option>'
    for performance in show.performances.order_by('date', 'time'):
        dt = datetime.datetime.combine(performance.date, performance.time)
        if dt >= datetime.datetime.now():
            dt = arrow.get(dt)
            html += f'<option value="{performance.id}">{dt:ddd, MMM D} at {dt:h:mm a} ({performance.tickets_available} tickets available)</option>'
    return HttpResponse(html)
    
@transaction.atomic
def sale_add_tickets(request):
    sale = _get_sale(request)
    sale_tickets_form = _create_sale_tickets_form(request.POST)
    sale_ticket_subforms = _create_sale_ticket_subforms(request.POST)
    if sale_tickets_form.is_valid() and sale_ticket_subforms.is_valid():

        # Get perforamnce and total number of tickets being purchased
        performance = get_object_or_404(Performance, pk = sale_tickets_form.cleaned_data['performance_id'])
        tickets_requested = sum([f.cleaned_data['quantity'] for f in sale_ticket_subforms])

        # Check if there are enought tickets available
        if tickets_requested <= performance.tickets_available:

            # Create a new sale if there is not one currently active
            if not sale:
                sale = _create_sale(request)

            # Add tickets
            for form in sale_ticket_subforms:

                # Get ticket type and quantity                
                ticket_type = get_object_or_404(TicketType, pk =  form.cleaned_data['type_id'])
                quantity = form.cleaned_data['quantity']

                # Add tickets to sale
                if quantity > 0:
                    for i in range(0, quantity):
                        ticket = Ticket(
                            sale = sale,
                            performance = performance,
                            description = ticket_type.name,
                            cost = ticket_type.price,
                        )
                        ticket.save()

                    # Confirm purchase
                    logger.info("%d x %s tickets added to sale: %s", quantity, ticket_type, performance)

            # Reset ticket form/formset
            sale_tickets_form = None
            sale_ticket_subforms = None

        # Insufficient tickets available
        else:
            logger.info("Tickets not available (%d requested, %d available): %s", tickets_requested, performance.tickets_available, performance)
            messages.error(request, f"There are only {performance.tickets_available} tickets available for this perfromance.")

    return _render_sale(request, sale_tickets_form, sale_ticket_subforms, None, None)

@transaction.atomic
def sale_update_extras(request):
    sale = _get_sale(request)
    sale_extras_form = _create_sale_extras_form(sale, request.POST)
    if sale_extras_form.is_valid():
        if not sale:
            sale = _create_sale(request)
        sale.buttons = sale_extras_form.cleaned_data['buttons']
        sale.save()
        fringers = sale_extras_form.cleaned_data['fringers']
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
        sale_extras_form = None
    return _render_sale(request, None, None, sale_extras_form, None)

@transaction.atomic
def sale_remove_performance(request, performance_id):
    sale = _get_sale(request)
    if sale:
        for ticket in sale.tickets.all():
            if ticket.performance_id == performance_id:
                ticket.delete()
        if sale.is_empty:
            sale.delete()
            sale = None
            request.session['sale_id'] = None
    else:
        logger.error('sale_remove_performance: no active sale')
    return _render_sale(request)

@transaction.atomic
def sale_remove_ticket(request, ticket_id):
    sale = _get_sale(request)
    if sale:
        try:
            ticket = Ticket.objects.get(pk = ticket_id)
            if ticket.sale == sale:
                ticket.delete()
            if sale.is_empty:
                sale.delete()
                sale = None
                request.session['sale_id'] = None
            else:
                logger.error('sale_remove_ticket: ticket %d not part of sale %d', ticket.id, sale.id)
        except Ticket.DoesNotExist:
            logger.error('sale_remove_ticket: ticket %d not found', ticket_id)
    else:
        logger.error('sale_remove_ticket: no active sale')
    return _render_sale(request)

@transaction.atomic
def sale_complete(request):
    sale = _get_sale(request)
    sale_form = _create_sale_form(sale, request.POST)
    if sale_form.is_valid():
        if not sale:
            logger.error('sale_complete: no active sale')
        elif sale.completed:
            logger.error('sale_complete: sale completed')
        else:
            sale.customer = sale_form.cleaned_data['customer']
            sale.amount = sale_form.cleaned_data['amount']
            sale.completed = datetime.datetime.now()
            sale.save()
            sale_form = None
    return _render_sale(request, None, None, None, sale_form)

@transaction.atomic
def sale_cancel(request):
    sale = _get_sale(request)
    if not sale:
        logger.error('sale_cancel: no active sale')
    elif sale.completed:
        logger.error('sale_cancel: sale completed')
    else:
        sale.delete()
        request.session['sale_id'] = None
    return _render_sale(request)

@transaction.atomic
def sale_new(request):
    sale = _get_sale(request)
    if not sale:
        logger.error('sale_new: no active sale')
    elif not sale.completed:
        logger.error('sale_new: sale not completed')
    else:
        sale = None
        request.session['sale_id'] = None
    return _render_sale(request)

# AJAX refund support
@transaction.atomic
def refund_add_ticket(request):
    refund = _get_refund(request)
    refund_ticket_form = _create_refund_ticket_form(request.POST)
    if refund_ticket_form.is_valid():
        try:
            ticket = Ticket.objects.get(pk = refund_ticket_form.cleaned_data['ticket_no'])
            if ticket.refund:
                refund_ticket_form.add_error('ticket_no', 'Ticket already refunded')
            elif ticket.fringer:
                refund_ticket_form.add_error('ticket_no', 'eFringer tickets cannot be refunded')
            else:
                if not refund:
                    refund = _create_refund(request)
                ticket.refund = refund
                ticket.save()
                refund_ticket_form = None
        except Ticket.DoesNotExist:
            refund_ticket_form.add_error('ticket_no', 'Ticket not found')
    return _render_refund(request, refund_ticket_form, None)

@transaction.atomic
def refund_remove_ticket(request, ticket_id):
    refund = _get_refund(request)
    if refund:
        try:
            ticket = Ticket.objects.get(pk = ticket_id)
            if ticket.refund == refund:
                ticket.refund = None
                ticket.save()
            if refund.is_empty:
                refund.delete()
                refund = None
                request.session['refund_id'] = None
            else:
                logger.error('refund_removeticket: ticket %d not part of refund %d', ticket.id, refund.id)
        except Ticket.DoesNotExist:
            logger.error('refund_removeticket: ticket %d not found', ticket_id)
    else:
        logger.error('refund_removeticket: no active refund')
    return _render_refund(request)

@transaction.atomic
def refund_complete(request):
    refund = _get_refund(request)
    refund_form = _create_refund_form(refund, request.POST)
    if refund_form.is_valid():
        if not refund:
            logger.error('refund_complete: no active refund')
        elif refund.completed:
            logger.error('refund_complete: refund completed')
        else:
            refund.customer = refund_form.cleaned_data['customer']
            refund.amount = refund_form.cleaned_data['amount']
            refund.reason = refund_form.cleaned_data['reason']
            refund.completed = datetime.datetime.now()
            refund.save()
            refund_form = None
    return _render_refund(request, None, refund_form)

@transaction.atomic
def refund_cancel(request):
    refund = _get_refund(request)
    if not refund:
        logger.error('refund_cancel: no active refund')
    elif refund.completed:
        logger.error('refund_cancel: refund completed')
    else:
        refund.delete()
        request.session['refund_id'] = None
    return _render_refund(request)

@transaction.atomic
def refund_new(request):
    refund = _get_refund(request)
    if not refund:
        logger.error('refund_new: no active refund')
    elif not refund.completed:
        logger.error('refund_new: refund not completed')
    else:
        refund = None
        request.session['refund_id'] = None
    return _render_refund(request)

# AJAX admission support
def admission_shows(request):

    box_office = _get_box_office(request)
    html = '<option value="0">-- Select show --</option>'
    for show in Show.objects.filter(venue__is_ticketed = True, venue__box_office = box_office):
        html += f'<option value="{show.id}">{show.name}</option>'
    return HttpResponse(html)

def admission_show_performances(request, show_id):

    show = get_object_or_404(Show, pk = show_id)
    html = '<option value="0">-- Select performance --</option>'
    for performance in show.performances.order_by('date', 'time'):
        dt = arrow.get(datetime.datetime.combine(performance.date, performance.time))
        html += f'<option value="{performance.id}">{dt:ddd, MMM D} at {dt:h:mm a} ({performance.tickets_available} tickets available)</option>'
    return HttpResponse(html)

def admission_performance_tickets(request, performance_id):

    # Get performance
    performance = get_object_or_404(Performance, pk = performance_id)

    # Get tickets for this performance (exclude tickets that are in a basket or part of an incomplete sale)
    tickets = Ticket.objects.filter(performance = performance)
    tickets = tickets.exclude(basket__isnull = False)
    tickets = tickets.exclude(fringer__isnull = True, sale__completed__isnull = True)

    # Render report
    context = {
        'performance': performance,
        'tickets': tickets.order_by('id'),
    }
    return render(request, 'boxoffice/admission_tickets.html', context)

# Report AJAX support
def report_summary(request, yyyymmdd):

    # Get sales and refunds for this box office
    box_office = _get_box_office(request)
    date = datetime.datetime.strptime(yyyymmdd, '%Y%m%d')
    sales = Sale.objects.filter(box_office = box_office, completed__date = date).order_by('id')
    refunds = Refund.objects.filter(box_office = box_office, completed__date = date).order_by('id')

    # Get aggregated figures
    sales_count = sales.count()
    sales_buttons = sales.aggregate(buttons = Coalesce(Sum('buttons'), 0))['buttons']
    sales_fringers = sales.aggregate(fringers = Coalesce(Sum('fringers__cost'), 0))['fringers']
    sales_tickets = sales.aggregate(tickets = Coalesce(Sum('tickets__cost'), 0))['tickets']
    sales_total = sales.aggregate(total = Coalesce(Sum('amount'), 0))['total']
    refunds_count = refunds.count()
    refunds_total = refunds.aggregate(total = Coalesce(Sum('amount'), 0))['total']

    # Render report
    context = {
        'sales_count': sales_count,
        'sales_buttons': sales_buttons,
        'sales_fringers': sales_fringers,
        'sales_tickets': sales_tickets,
        'sales_total': sales_total,
        'refunds_count': refunds_count,
        'refunds_total': refunds_total,
        'balance': sales_total - refunds_total,
    }
    return render(request, 'boxoffice/report_summary.html', context)

def report_sales(request, yyyymmdd):

    # Get completed sales for this box office
    box_office = _get_box_office(request)
    date = datetime.datetime.strptime(yyyymmdd, '%Y%m%d')
    sales = Sale.objects.filter(box_office = box_office, completed__date = date).order_by('id')

    # Render report
    context = {
        'box_office': box_office,
        'sales': sales,
    }
    return render(request, 'boxoffice/report_sales.html', context)

def report_sale_detail(request, sale_id):
    sale = get_object_or_404(Sale, pk = sale_id)
    context = {
        'sale': sale,
    }
    return render(request, 'boxoffice/report_sale_detail.html', context)

def report_refunds(request, yyyymmdd):

    # Get completed refunds for this box office
    box_office = _get_box_office(request)
    date = datetime.datetime.strptime(yyyymmdd, '%Y%m%d')
    refunds = Refund.objects.filter(box_office = box_office, completed__date = date).order_by('id')

    # Render report
    context = {
        'box_office': box_office,
        'refunds': refunds,
    }
    return render(request, 'boxoffice/report_refunds.html', context)

def report_refund_detail(request, refund_id):
    refund = get_object_or_404(Refund, pk = refund_id)
    context = {
        'refund': refund,
    }
    return render(request, 'boxoffice/report_refund_detail.html', context)
