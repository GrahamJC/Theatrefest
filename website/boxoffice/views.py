import datetime
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View
from django.forms import formset_factory, modelformset_factory
from django.http import JsonResponse

from program.models import Show, Performance
from tickets.models import BoxOffice, Sale, TicketType, Ticket, Fringer

from .forms import TicketsForm, TicketSubForm, ExtrasForm, SaleForm

# Logging
import logging
logger = logging.getLogger(__name__)


class SelectView(LoginRequiredMixin, View):

    def get(self,request):

        # Let user select a box office
        context = {
            'box_offices': BoxOffice.objects.all(),
        }
        return render(request, 'boxoffice/select.html', context)

    @transaction.atomic
    def post(self, request):

        # Save selected box office
        request.session['box_office_id'] = request.POST['box_office_id']

        # Go to box office home page
        return redirect(reverse('boxoffice:sale'))


class SaleView(LoginRequiredMixin, View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tickets_form = None
        self.ticket_subforms = None
        self.extras_form = None
        self.sale_form = None

    def get_session_data(self, request):
        # Get the current box office and sale
        try:
            self.box_office = BoxOffice.objects.get(pk = request.session.get('box_office_id', None))
        except BoxOffice.DoesNotExist:
            self.box_office = None
        try:
            self.sale = Sale.objects.get(pk = request.session.get('sale_id', None))
        except Sale.DoesNotExist:
            self.sale = None

    def ensure_sale(self, request):
        # Create a new sale if there isn't one already
        if not self.sale:
            self.sale = Sale(
                box_office = self.box_office,
                user = request.user
            )
            self.sale.save()
            request.session['sale_id'] = self.sale.id

    def create_ticket_subforms(self, post_data = None):
        # Build and populate ticket formset
        TicketFormset = formset_factory(TicketSubForm, extra = 0)
        initial_data = [{'type_id': t.id, 'name': t.name, 'price': t.price, 'quantity': 0} for t in TicketType.objects.filter(is_admin = False)]
        return TicketFormset(post_data, initial=initial_data)

    def render_sale(self, request):
        # If the current sale is empty delete it
        if self.sale and self.sale.is_empty:
            self.sale.delete()
            self.sale = None
            request.session['sale_id'] = None

        # Create forms if they don't already exist
        if not self.tickets_form:
            self.tickets_form = TicketsForm()
        if not self.ticket_subforms:
            self.ticket_subforms = self.create_ticket_subforms()
        if not self.extras_form:
            initial_data = { 'buttons': 0, 'fringers': 0 }
            if self.sale:
                initial_data['buttons'] = self.sale.buttons
                initial_data['fringers'] = self.sale.fringers.count() or 0
            self.extras_form = ExtrasForm(initial = initial_data)
        if not self.sale_form:
            self.sale_form = SaleForm()
        context = {
            'box_office': self.box_office,
            'tickets_form': self.tickets_form,
            'ticket_subforms': self.ticket_subforms,
            'extras_form': self.extras_form,
            'sale_form': self.sale_form,
            'sale': self.sale,
        }
        return render(request, 'boxoffice/sale.html', context)

    def get(self,request):

        # Get the current box office and sale
        self.get_session_data(request)
        if not self.box_office:
            return redirect(reverse('boxoffice:select'))

        # Render box office sale page
        return self.render_sale(request)

    @transaction.atomic
    def post(self, request):

        # Get the current box office and sale
        self.get_session_data(request)
        if not self.box_office:
            return redirect(reverse('boxoffice:select'))

        # Process action
        action = request.POST['action']
        if action == 'AddTickets':

            # Bind ticket form/formset and check for errors
            self.ticket_form = TicketsForm(request.POST)
            self.ticket_subforms = self.create_ticket_subforms(request.POST)
            if self.ticket_form.is_valid() and self.ticket_subforms.is_valid():

                # Get performance
                performance = get_object_or_404(Performance, pk = self.ticket_form.cleaned_data['performance_id'])

                # Get total number of tickets being purchased
                tickets_requested = sum([f.cleaned_data['quantity'] for f in self.ticket_subforms])
                if tickets_requested <= performance.tickets_available:

                    # Create a new sale if there is not one currently active
                    self.ensure_sale(request)

                    # Add tickets
                    for form in self.ticket_subforms:

                        # Get ticket type and quantity                
                        ticket_type = get_object_or_404(TicketType, pk =  form.cleaned_data['type_id'])
                        quantity = form.cleaned_data['quantity']

                        # Add tickets to sale
                        if quantity > 0:
                            for i in range(0, quantity):
                                ticket = Ticket(
                                    sale = self.sale,
                                    performance = performance,
                                    description = ticket_type.name,
                                    cost = ticket_type.price,
                                )
                                ticket.save()

                            # Confirm purchase
                            logger.info("%d x %s tickets added to sale: %s", quantity, ticket_type, performance)

                    # Reset ticket form/formset
                    self.ticket_form = None
                    self.ticket_subforms = None

                # Insufficient tickets available
                else:
                    logger.info("Tickets not available (%d requested, %d available): %s", tickets_requested, performance.tickets_available, performance)
                    messages.error(request, f"There are only {performance.tickets_available} tickets available for this perfromance.")

        elif action == 'UpdateExtras':

            # Bind extras form and check for errors
            self.extras_form = ExtrasForm(request.POST)
            if self.extras_form.is_valid():

                # Create a new sale if there is not one currently active
                self.ensure_sale(request)

                # Update buttons
                self.sale.buttons = self.extras_form.cleaned_data['buttons']
                self.sale.save()

                # Update fringers
                fringers = self.extras_form.cleaned_data['fringers']
                while (self.sale.fringers.count() or 0) > fringers:
                    self.sale.fringers.first().delete()
                while (self.sale.fringers.count() or 0) < fringers:
                    fringer = Fringer(
                        description = '6 shows for £18',
                        shows = 6,
                        cost = 18,
                        sale = self.sale,
                    )
                    fringer.save()

                # Reset extras form
                self.extras_form = None

        elif action == "CompleteSale":

            # Complete the current sale
            if self.sale:
                self.sale_form = SaleForm(request.POST)
                if self.sale_form.is_valid():
                    self.sale.customer = self.sale_form.cleaned_data['customer']
                    self.sale.completed = datetime.datetime.now()
                    self.sale.save()
                    logger.info("Sale completed: %s", self.sale.id)

        elif action == "CancelSale":

            # Delete the current sale
            if self.sale:
                logger.info("Sale cancelled: %d", self.sale.id)
                self.sale.delete()
                self.sale = None
                request.session['sale_id'] = None

        elif action == "NewSale":

            # Start a new sale
            if self.sale:
                self.sale = None
                request.session['sale_id'] = None
                logger.info("New sale started")

        # Render box office sale page
        return self.render_sale(request)


@transaction.atomic
def sale_remove_performance(request, performance_id):
    sale = Sale.objects.get(pk = request.session.get('sale_id', None))
    if sale:
        for ticket in sale.tickets.filter(performance_id = performance_id):
            ticket.delete()
    return redirect(reverse('boxoffice:sale'))


@transaction.atomic
def sale_remove_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk =  ticket_id)
    ticket.delete()
    return redirect(reverse('boxoffice:sale'))


import os
from django.conf import settings
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.units import cm
from reportlab.lib import colors

class SalePrintView(LoginRequiredMixin, View):

    def get(self, request, sale_id):

        # Get sale to be printed
        sale = get_object_or_404(Sale, pk = sale_id)

        # Create receipt as a Platypus story
        response = HttpResponse(content_type = "application/pdf")
        response["Content-Disposition"] = f"attachment; filename=sale{sale.id}.pdf"
        doc = SimpleDocTemplate(
            response,
            pagesize = portrait(A4),
            leftMargin = 2.5*cm,
            rightMargin = 2.5*cm,
            topMargin = 2.5*cm,
            bottomMargin = 2.5*cm,
        )
        styles = getSampleStyleSheet()
        story = []

        # Theatrefest banner
        banner = Image(os.path.join(settings.STATIC_ROOT, "BridgeBanner.png"), width = 16*cm, height = 4*cm)
        banner.hAlign = 'CENTER'
        story.append(banner)
        story.append(Spacer(1, 1*cm))

        # Customer and sale number
        table = Table(
            (
                (Paragraph("<para><b>Customer:</b></para>", styles['Normal']), sale.customer),
                (Paragraph("<para><b>Sale no:</b></para>", styles['Normal']), sale.id),
            ),
            colWidths = (4*cm, 12*cm),
            hAlign = 'LEFT'
        )
        story.append(table)
        story.append(Spacer(1, 1*cm))

        # Buttons
        if sale.buttons or sale.fringers.count():
            tableData = []
            if sale.buttons:
                tableData.append((Paragraph("<para><b>Buttons</b></para>", styles['Normal']), sale.buttons, f"£{sale.button_cost}"))
            if sale.fringers.count():
                tableData.append((Paragraph("<para><b>Fringers</b></para>", styles['Normal']), sale.fringers.count(), f"£{sale.fringer_cost}"))
            table = Table(
                tableData,
                colWidths = (8*cm, 4*cm, 4*cm),
                hAlign = 'LEFT',
                style = (
                    ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                )
            )
            story.append(table)
            story.append(Spacer(1, 0.5*cm))

        # Tickets
        is_first = True
        for performance in sale.performances:
            if not is_first:
                story.append(Spacer(1, 0.5*cm))
            is_first = False
            tableData = []
            tableData.append((Paragraph(f"<para><b>{performance['show']}</b></para>", styles['Normal']), "", "", ""))
            tableData.append((f"{performance['date']:%a, %e %b} at {performance['time']:%I:%M %p}", "", "", ""))
            for ticket in performance['tickets']:
                tableData.append((f"{ticket['id']}", "", ticket['description'], f"£{ticket['cost']}"))
            table = Table(
                tableData,
                colWidths = (4*cm, 4*cm, 4*cm, 4*cm),
                hAlign = 'LEFT',
                style = (
                    ('SPAN', (0, 0), (3, 0)),
                    ('SPAN', (0, 1), (3, 1)),
                    ('ALIGN', (0, 2), (0, -1), 'RIGHT'),
                    ('ALIGN', (3, 2), (3, -1), 'RIGHT'),
                )
            )
            story.append(table)

        # Total
        story.append(Spacer(1, 1*cm))
        table = Table(
            (
                ("", Paragraph("<para><b>Total:</b></para>", styles['Normal']), f"£{sale.total_cost}"),
            ),
            colWidths = (8*cm, 4*cm, 4*cm),
            hAlign = 'LEFT',
            style = (
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
            )
        )
        story.append(table)

        # Create PDF document and return it
        doc.build(story)
        return response

