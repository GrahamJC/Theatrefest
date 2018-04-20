from datetime import datetime, date, time

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.forms import formset_factory, modelformset_factory
from django.utils import timezone

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from crispy_forms.bootstrap import FormActions, StrictButton, FieldWithButtons

from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.lib import colors

from .models import Sale, Basket, FringerType, Fringer, TicketType, Ticket
from .forms import BuyTicketForm, RenameFringerForm, BuyFringerForm
from program.models import Show, Performance

# Logging
import logging
logger = logging.getLogger(__name__)

# Stripe interface
import stripe
stripe.api_key = settings.STRIPE_PRIVATE_KEY


class ShowView(LoginRequiredMixin, View):

    def get(self, request):

        # Get tickets
        tickets_current = []
        tickets_past = []
        for ticket in Ticket.objects.filter(user = request.user):
            if datetime.combine(ticket.performance.date, ticket.performance.time) > datetime(2018, 6, 30): #datetime.now():
                tickets_current.append(ticket)
            else:
                tickets_past.append(ticket)

        # Display tickets
        context = {
            'tickets_current': tickets_current,
            'tickets_past': tickets_past,
        }
        return render(request, "tickets/show.html", context)

class TheatrefestBuyView(LoginRequiredMixin, View):

    def get(self, request, theatrefest_id, yyyymmdd, hhmm):

        # Get show
        show = get_object_or_404(Show, theatrefest_ID = theatrefest_id)

        # Get performance
        date = datetime.strptime(yyyymmdd, "%Y%m%d").date()
        time = datetime.strptime(hhmm, "%H%M").time()
        performance = get_object_or_404(Performance, show = show, date = date, time = time)

        # Show buy page
        return redirect(f"/tickets/buy/{performance.id}")


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

        # Check if using fringers
        action = request.POST.get("action")
        if action == "fringer":

            # Check if there are still enough tickets available
            tickets_requested = len(request.POST.getlist('fringer_id'))
            if tickets_requested <= performance.tickets_available:

                # Process each checked fringer
                for fringer_id in request.POST.getlist('fringer_id'):

                    # Get fringer
                    fringer = Fringer.objects.get(pk = int(fringer_id))

                    # Create ticket
                    ticket = Ticket(
                        user = request.user,
                        performance = performance,
                        description = "eFringer",
                        cost = 0,
                        fringer = fringer,
                    )
                    ticket.save()

                    # Confirm purchase
                    logger.info("Ticket purchased with eFringer (%s): %s", fringer.name, performance)
                    messages.success(request, f"Ticket purchased with eFringer {fringer.name}")

            # Insufficient tickets available
            else:
                logger.info("Tickets not available (%d requested, %d available): %s", tickets_requested, performance.tickets_available, performance)
                messages.error(request, f"There are only {performance.tickets_available} tickets available for this perfromance.")

            # Reset ticket type formset
            ticket_formset = self.get_ticket_formset(None, ticket_types)

        # Must be add to basket
        elif action == "add":

            # Create ticket type formset
            ticket_formset = self.get_ticket_formset(request.POST, ticket_types)

            # Check for errors
            if ticket_formset.is_valid():

                # Get total number of tickets being purchased
                tickets_requested = sum([f.cleaned_data['quantity'] for f in ticket_formset])
                if tickets_requested <= performance.tickets_available:

                    # Process ticket types
                    for form in ticket_formset:

                        # Get ticket type and quantity                
                        ticket_type = get_object_or_404(TicketType, pk =  form.cleaned_data['id'])
                        quantity = form.cleaned_data['quantity']

                        # Create tickets and add to basket
                        if quantity > 0:
                            for i in range(0, quantity):
                                ticket = Ticket(
                                    performance = performance,
                                    description = ticket_type.name,
                                    cost = ticket_type.price,
                                    user = request.user,
                                    basket = basket,
                                )
                                ticket.save()

                            # Confirm purchase
                            logger.info("%d x %s tickets added to basket: %s", quantity, ticket_type, performance)
                            messages.success(request, f"{quantity} x {ticket_type} tickets added to basket.")

                    # Reset ticket type formset
                    ticket_formset = self.get_ticket_formset(None, ticket_types)

                # Insufficient tickets available
                else:
                    logger.info("Tickets not available (%d requested, %d available): %s", tickets_requested, performance.tickets_available, performance)
                    messages.error(request, f"There are only {performance.tickets_available} tickets available for this perfromance.")

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

    form_tag = False
    form_class = "form-horizontal"
    label_class = "col-xs-12 col-sm-2"
    field_class= "col-xs-12, col-sm-10"
    layout = Layout(
        'type',
        'name', 
    )

class FringersView(LoginRequiredMixin, View):

    def get(self, request):

        # Create fringer formset
        FringerFormSet = modelformset_factory(Fringer, form = RenameFringerForm, extra = 0)
        formset = FringerFormSet(queryset = Fringer.objects.filter(user = request.user, basket = None))

        # Get fringer types and create buy form
        fringer_types = FringerType.objects.filter(is_online = True)
        buy_form = BuyFringerForm(request.user, fringer_types)
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

        # Get the action and basket
        action = request.POST.get("action")
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
                    logger.info("eFringer renamed to %s", fringer.name)
                    messages.success(request, f"eFringer renamed to {fringer.name}")

                # Reset formset
                formset = None

        # Check for buying
        elif action == "Add":

            # Get fringer types and create form
            fringer_types = FringerType.objects.filter(is_online = True)
            buy_form = BuyFringerForm(request.user, fringer_types, request.POST)

            # Check for errors
            if buy_form.is_valid():

                # Get fringer type
                buy_type = get_object_or_404(FringerType, pk = int(buy_form.cleaned_data['type']))
                buy_name = buy_form.cleaned_data['name']
                if not buy_name:
                    fringer_count = Fringer.objects.filter(user = request.user).count()
                    buy_name = f"eFringer{fringer_count + 1}"

                # Create new fringer and add to basket
                fringer = Fringer(
                    user = request.user,
                    name = buy_name if buy_name else buy_type.name,
                    date_time = timezone.now(),
                    description = buy_type.description,
                    shows = buy_type.shows,
                    cost = buy_type.price,
                    basket = basket,
                )
                fringer.save()
                logger.info("eFringer %s (%s) added to basket", fringer.name, fringer.description)
                messages.success(request, f"Fringer {fringer.name} ({fringer.description}) added to basket")

                # Reset form
                buy_form = None

        # Create formset and form if not already done
        if not formset:
            FringerFormSet = modelformset_factory(Fringer, form = RenameFringerForm, extra = 0)
            formset = FringerFormSet(queryset = Fringer.objects.filter(user = request.user, basket = None))
        if not buy_form:
            fringer_types = FringerType.objects.filter(is_online = True)
            buy_form = BuyFringerForm(request.user, fringer_types)

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
            'basket': basket,
            "stripe_key": settings.STRIPE_PUBLIC_KEY,
        }
        return render(request, "tickets/checkout.html", context)

    @transaction.atomic
    def post(self, request):

        # Get basket
        basket = request.user.basket

        # Check that tickets are still available
        tickets_available = True
        for p in basket.tickets.values('performance').annotate(count = Count('performance')):
            performance = Performance.objects.get(pk = p["performance"])
            if p["count"] > performance.tickets_available:
                messages.error(request, f"Your basket contains {p['count']} tickets for {performance} but there are only {performance.tickets_available} tickets available.")
                logger.warn("Basket contains %d tickets but only %d available: %s", p["count"], performance.tickets_available, performance)
                tickets_available = False
        if not tickets_available:
            messages.error(request, f"Your card has not been charged.")
        else:
            # Complete purchase and charge credit card
            try:
                # Create Stripe charge
                stripe_token = request.POST.get("stripeToken")
                charge = stripe.Charge.create(
                    source = stripe_token,
                    amount = basket.stripe_charge_pence,
                    currency = "GBP",
                    description = "Theatrefest tickets",
                    receipt_email = basket.user.email
                )
                logger.info("Credit card charged £%.2f (%s)", basket.stripe_charge, stripe_token)
                messages.success(request, f"Purchase complete. Your card has been charged £{basket.stripe_charge}.")

                # Create a new sale
                sale = Sale(
                    user = request.user,
                )
                sale.save()

                # Complete purchase of fringers by removing them from the basket and adding them to the sale
                for fringer in basket.fringers.all():
                    fringer.basket = None
                    fringer.sale = sale
                    fringer.save()
                    logger.info("Purchase complete: eFringer %s (%s)", fringer.name, fringer.description)

                # Complete purchase of tickets by removing them from the basket
                for ticket in basket.tickets.all():
                    ticket.basket = None
                    ticket.sale = sale
                    ticket.save()
                    logger.info("Purchase complete: %s ticket for %s", ticket.description, ticket.performance)

            except stripe.error.CardError as ce:
                logger.exception("Credit card charge failure")
                return False, ce

        # Redisplay checkout
        context = {
            'basket': basket,
            "stripe_key": settings.STRIPE_PUBLIC_KEY,
        }
        return render(request, "tickets/checkout.html", context)


class RemoveFringerView(LoginRequiredMixin, View):

    @transaction.atomic
    def get(self, request, fringer_id):

        # Get basket and fringer to be removed
        basket = request.user.basket
        fringer = get_object_or_404(Fringer, pk = fringer_id)

        # Delete fringer
        logger.info("eFringer %s (%s) removed from basket", fringer.name, fringer.description)
        messages.success(request, f"Fringer {fringer.name} ({fringer.description}) removed from basket")
        fringer.delete()

        # Redisplay checkout
        context = {
            'basket': basket,
            "stripe_key": settings.STRIPE_PUBLIC_KEY,
        }
        return render(request, "tickets/checkout.html", context)


class RemovePerformanceView(LoginRequiredMixin, View):

    @transaction.atomic
    def get(self, request, performance_id):

        # Get basket and performance
        basket = request.user.basket
        performance = get_object_or_404(Performance, pk = performance_id)

        # Delete all tickets for the performance
        for ticket in basket.tickets.filter(performance = performance):
            logger.info("%s ticket for %s removed from basket", ticket.description, ticket.performance)
            ticket.delete()
        messages.success(request, f"{performance} removed from basket")

        # Redisplay checkout
        context = {
            'basket': basket,
            "stripe_key": settings.STRIPE_PUBLIC_KEY,
        }
        return render(request, "tickets/checkout.html", context)


class RemoveTicketView(LoginRequiredMixin, View):

    @transaction.atomic
    def get(self, request, ticket_id):

        # Get basket and ticket to be removed
        basket = request.user.basket
        ticket = get_object_or_404(Ticket, pk = ticket_id)

        # Delete ticket
        logger.info("%s ticket for %s removed from basket", ticket.description, ticket.performance)
        messages.success(request, f"{ticket.description} ticket for {ticket.performance} removed from basket")
        ticket.delete()

        # Redisplay checkout
        context = {
            'basket': basket,
            "stripe_key": settings.STRIPE_PUBLIC_KEY,
        }
        return render(request, "tickets/checkout.html", context)


class CancelTicketView(LoginRequiredMixin, View):

    @transaction.atomic
    def get(self, request, ticket_id):

        # Get ticket to be cancelled
        ticket = get_object_or_404(Ticket, pk = ticket_id)

        # Delete ticket
        logger.info("%s ticket for %s cancelled", ticket.description, ticket.performance)
        messages.success(request, f"{ticket.description} ticket for {ticket.performance} cancelled")
        ticket.delete()

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
            [ticket.performance.date.strftime("%a, %d %b") + " at " + ticket.performance.time.strftime("%H:%M"), ticket.performance.show.venue.name],
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
