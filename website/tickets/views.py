from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View
from django.forms import formset_factory, modelformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from crispy_forms.bootstrap import FormActions, StrictButton, FieldWithButtons

from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.lib import colors

from program.models import Performance
from .models import BoxOffice, Basket, FringerType, Fringer, TicketType, Ticket
from .forms import BuyTicketForm, RenameFringerForm, BuyFringerForm


class ShowView(LoginRequiredMixin, View):

    def get(self, request):

        # Get tickets
        tickets = Ticket.objects.filter(user = request.user)

        # Display tickets
        context = {
            'tickets': tickets,
        }
        return render(request, "tickets/show.html", context)


class BuyView(LoginRequiredMixin, View):

    def get_ticket_formset(self, post_data, ticket_types):
        TicketFormset = formset_factory(BuyTicketForm, extra = 0)
        initial_data = [{'id': t.id, 'name': t.name, 'price': t.price, 'quantity': 0} for t in ticket_types]
        return TicketFormset(post_data, initial = initial_data)

    def get(self, request, performance_id):

        # Get basket and performance and ticket types
        basket = request.user.basket
        performance = get_object_or_404(Performance, pk = performance_id)
        ticket_types = TicketType.objects.filter(is_online = True)

        # Get fringers available for this perfromance
        fringers = Fringer.get_available(request.user, performance)

        # Create ticket type formset
        ticket_formset = self.get_ticket_formset(None, ticket_types)

        # Display buy page
        context = {
            'basket': basket,
            'performance': performance,
            'fringers': fringers,
            'ticket_formset': ticket_formset,
        }
        return render(request, "tickets/buy.html", context)

    @transaction.atomic
    def post(self, request, performance_id):

        # Get basket, performance and ticket types
        basket = request.user.basket
        performance = get_object_or_404(Performance, pk = performance_id)
        ticket_types = TicketType.objects.filter(is_online = True)

        # Get online box office
        box_office = get_object_or_404(BoxOffice, name = 'Online')

        # Check if using fringers
        action = request.POST.get("action")
        if action == "fringer":

            # Process each checked fringer
            if len(request.POST.getlist('fringer_id')) <= performance.tickets_available:
                for fringer_id in request.POST.getlist('fringer_id'):

                    # Get fringer
                    fringer = Fringer.objects.get(pk = int(fringer_id))

                    # Create ticket
                    ticket = Ticket(
                        user = request.user,
                        box_office = box_office,
                        performance = performance,
                        date_time = datetime.now(),
                        description = "Fringer",
                        cost = 0,
                        fringer = fringer,
                    )
                    ticket.save()

                    # Confirm purchase
                    messages.success(request, "Ticket purchased with fringer {0}".format(fringer.name))

            # Insufficient tickets available
            else:
                messages.error(request, "There are only {0} tickets available".format(performance.tickets_available))

            # Create ticket type formset
            ticket_formset = self.get_ticket_formset(None, ticket_types)

        # Must be add to basket
        elif action == "add":

            # Create ticket type formset
            ticket_formset = self.get_ticket_formset(request.POST, ticket_types)

            # Check for errors
            if ticket_formset.is_valid():

                # Get total number of tickets being purchased
                total_quantity = sum([f.cleaned_data['quantity'] for f in ticket_formset])
                if total_quantity <= performance.tickets_available:

                    # Process tickets
                    for form in ticket_formset:

                        # Get ticket type and quantity                
                        ticket_type = get_object_or_404(TicketType, pk =  form.cleaned_data['id'])
                        quantity = form.cleaned_data['quantity']

                        # Create tickets and add to basket
                        for i in range(0, quantity):
                            ticket = Ticket(
                                user = request.user,
                                box_office = box_office,
                                performance = performance,
                                date_time = datetime.now(),
                                description = ticket_type.name,
                                cost = ticket_type.price,
                            )
                            ticket.save()
                            basket.add_item(ticket)

                        # Confirm purchase
                        if quantity:
                            messages.success(request, "{0} x {1} tickets added to basket".format(quantity, ticket_type.name))

                # Insufficient tickets available
                else:
                    messages.error(request, "There are only {0} tickets available".format(performance.tickets_available))

        # Get fringers available for this perfromance
        fringers = Fringer.get_available(request.user, performance)

        # Display buy page
        context = {
            'basket': basket,
            'performance': performance,
            'fringers': fringers,
            'ticket_formset': ticket_formset,
        }
        return render(request, "tickets/buy.html", context)


class BuyFringerFormHelper(FormHelper):

    form_class = "form-horizontal"
    label_class = "col-xs-12 col-sm-2"
    field_class= "col-xs-12, col-sm-10"
    layout = Layout(
        'type',
        'name', 
        Submit("action", "Add to Basket"),
    )

class FringersView(LoginRequiredMixin, View):

    def get(self, request):

        # Create fringer formset
        FringerFormSet = modelformset_factory(Fringer, form = RenameFringerForm, extra = 0)
        formset = FringerFormSet(queryset = Fringer.objects.filter(user = request.user, basket = None))

        # Get fringer types and create buy form
        fringer_types = FringerType.objects.filter(is_online = True)
        buy_form = BuyFringerForm(fringer_types)
        buy_form.use_required_attribute = False
        buy_form.helper = BuyFringerFormHelper()

        # Display fringers
        context = {
            'basket': request.user.basket,
            'formset': formset,
            'buy_form': buy_form,
        }
        return render(request, "tickets/fringers.html", context)

    @transaction.atomic
    def post(self, request):

        # Get the action, box-office and basket
        action = request.POST.get("action")
        box_office = get_object_or_404(BoxOffice, name = 'Online')
        basket = request.user.basket
        formset = None
        buy_form = None

        # Check for rename
        if action == "Rename":

            # Create fringer formset
            FringerFormSet = modelformset_factory(Fringer, form = RenameFringerForm, extra = 0)
            formset = FringerFormSet(request.POST, queryset = Fringer.objects.filter(user = request.user, basket = None))

            # Check for errors
            if formset.is_valid():

                # Save changes
                for fringer in formset.save():
                    messages.success(request, "Fringer renamed to {0}".format(fringer.name))

        # Check for buying
        elif action == "Add to Basket":

            # Get fringer types and create form
            fringer_types = FringerType.objects.filter(is_online = True)
            buy_form = BuyFringerForm(fringer_types, request.POST)

            # Check for errors
            if buy_form.is_valid():

                # Get fringer type
                buy_type = get_object_or_404(FringerType, pk = int(buy_form.cleaned_data['type']))
                buy_name = buy_form.cleaned_data['name']

                # Create new fringer and add to basket
                fringer = Fringer(
                    user = request.user,
                    name = buy_name if buy_name else buy_type.name,
                    box_office = box_office,
                    date_time = datetime.now(),
                    description = buy_type.description,
                    shows = buy_type.shows,
                    cost = buy_type.price,
                )
                fringer.save()
                basket.add_item(fringer)
                messages.success(request, "Fringer ({0}) added to basket".format(fringer.description))

        # Create formset and form if not already done
        if not formset:
            FringerFormSet = modelformset_factory(Fringer, form = RenameFringerForm, extra = 0)
            formset = FringerFormSet(queryset = Fringer.objects.filter(user = request.user, basket = None))
        if not buy_form:
            fringer_types = FringerType.objects.filter(is_online = True)
            buy_form = BuyFringerForm(fringer_types)

        # Add crispy forms helper to buy form
        buy_form.helper = BuyFringerFormHelper()

        # Redisplay with confirmation
        context = {
            'basket': basket,
            'formset': formset,
            'buy_form': buy_form,
        }
        return render(request, "tickets/fringers.html", context)


class CheckoutView(LoginRequiredMixin, View):

    def get(self, request):

        # Get basket
        basket = request.user.basket

        # Display basket
        context = {
            'basket': basket
        }
        return render(request, "tickets/checkout.html", context)

    @transaction.atomic
    def post(self, request):

        # Get basket
        basket = request.user.basket

        # Complete purchase of fringers (i.e. remove them from the basket)
        for fringer in basket.fringers.all():
            basket.remove_item(fringer)
            messages.success(request, "Purchase complete: {0}".format(fringer.description))

        # Complete purchase of tickets (i.e. remove them from the basket)
        for ticket in basket.tickets.all():
            basket.remove_item(ticket)
            messages.success(request, "Purchase complete: {0}".format(ticket))

        # Redisplay empty basket and purchase confirmation
        context = {
            'basket': basket,
        }
        return render(request, "tickets/checkout.html", context)


class RemoveFringerView(LoginRequiredMixin, View):

    @transaction.atomic
    def get(self, request, fringer_id):

        # Get basket and fringer to be removed
        basket = request.user.basket
        fringer = get_object_or_404(Fringer, pk = fringer_id)

        # Delete fringer
        fringer.delete()
        messages.success(request, "Fringer removed from basket")


        # Redisplay checkout
        context = {
            'basket': basket,
        }
        return render(request, "tickets/checkout.html", context)


class RemoveTicketView(LoginRequiredMixin, View):

    @transaction.atomic
    def get(self, request, ticket_id):

        # Get basket and ticket to be removed
        basket = request.user.basket
        ticket = get_object_or_404(Ticket, pk = ticket_id)

        # Delete ticket
        ticket.delete()
        messages.success(request, "Ticket removed from basket")

        # Redisplay checkout
        context = {
            'basket': basket,
        }
        return render(request, "tickets/checkout.html", context)


class CancelTicketView(LoginRequiredMixin, View):

    @transaction.atomic
    def get(self, request, ticket_id):

        # Get ticket to be cancelled
        ticket = get_object_or_404(Ticket, pk = ticket_id)

        # Delete ticket
        ticket.delete()
        messages.success(request, "Ticket cancelled")

        # Redisplay tickets
        context = {
            'tickets': Ticket.objects.filter(user = request.user),
        }
        return render(request, "tickets/show.html", context)


class PrintTicketView(LoginRequiredMixin, View):

    PAGE_WIDTH = defaultPageSize[0]
    PAGE_HEIGHT = defaultPageSize[1]
    styles = getSampleStyleSheet()

    TICKET_STYLE = TableStyle()
    TICKET_STYLE.add('BOX', (0, 0), (-1, -1), 2, colors.green)
    TICKET_STYLE.add('ALIGN', (1, 0), (-1, -1), "RIGHT")

    def firstPage(canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Bold', 16)
        canvas.drawCentredString(PrintTicketView.PAGE_WIDTH / 2, PrintTicketView.PAGE_HEIGHT - 100, "Hello World!")
        canvas.setFont('Times-Roman', 9)
        canvas.drawString(inch, 0.75 * inch, "First page")
        canvas.restoreState()

    def laterPage(canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 9)
        canvas.drawString(inch, 0.75 * inch, "Page no: {0}".format(doc.page))
        canvas.restoreState()

    def add_ticket(self, story, ticket):
        data = [
            ["Theatrefest 2018", ticket.id],
            [ticket.performance.show.name, "{0} {1}".format(ticket.user.first_name, ticket.user.last_name)],
            [ticket.performance.date_time.strftime("%a, %d %b at %H:%M"), ticket.performance.show.venue.name],
        ]
        table = Table(data, colWidths = [(PrintTicketView.PAGE_WIDTH - 100)/ 2, (PrintTicketView.PAGE_WIDTH -100)/ 2], style = PrintTicketView.TICKET_STYLE)
        story.append(table)

    def get(self, request, ticket_id):

        # Get ticket to be printed
        ticket = get_object_or_404(Ticket, pk = ticket_id)

        # Create reponse for PDF document
        response = HttpResponse(content_type = "application/pdf")
        response["Content-Disposition"] = "attachment; filename=ticket{0}.pdf".format(ticket.id)

        # Create Platypus story
        story = []
        for ticket in request.user.tickets.all():
            self.add_ticket(story, ticket)

        # Create PDF document and return it
        doc = SimpleDocTemplate(response)
        doc.build(story)
        return response
