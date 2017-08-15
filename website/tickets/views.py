from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.forms import modelformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from crispy_forms.bootstrap import FormActions, StrictButton, FieldWithButtons

from catalog.models import Performance
from .models import BoxOffice, Basket, FringerType, Fringer, TicketType, Ticket
from .forms import BuyFringerForm


class BuyView(LoginRequiredMixin, View):

    def get(self, request, performance_id):

        # Get performance
        basket = request.user.basket
        performance = get_object_or_404(Performance, pk = performance_id)

        # Get available fringers
        fringers = request.user.fringers.all()

        # Get ticket types
        ticket_types = TicketType.objects.filter(is_online = True)

        # Display buy page
        context = {
            'basket': basket,
            'performance': performance,
            'fringers': fringers,
            'ticket_types': ticket_types,
        }
        return render(request, "tickets/buy.html", context)

    def post(self, request, performance_id):

        # Get box office and performance
        action = request.POST.get("action")
        box_office = get_object_or_404(BoxOffice, name = 'Online')
        basket = request.user.basket
        performance = get_object_or_404(Performance, pk = performance_id)
        ticket_types = TicketType.objects.filter(is_online = True)

        # Get available fringers
        fringers = request.user.fringers.all()

        # Check if using fringers
        if action == "fringer":

            # Check to see if each fringer is being used
            for fringer in fringers:
                if "fringer{0}".format(fringer.id) in request.POST:

                    # Create ticket
                    ticket = Ticket(
                        user = request.user,
                        box_office = box_office,
                        performance = performance,
                        date_time = datetime.now(),
                        description = "eFringer",
                        cost = 0,
                        fringer = fringer,
                    )
                    ticket.save()

                    # Confirm purchase
                    messages.success(request, "Ticket purchased with fringer {0}".format(fringer.name))

        # Must be add to basket
        elif action == "add":

            # Check each ticket type
            for ticket_type in ticket_types:
                quantity = int(request.POST.get(ticket_type.name))
                if quantity:

                    # Create tickets
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

                    # Add to basket
                    basket.add_item(ticket)

                    # Confirm purchase
                    messages.success(request, "{0} x {1} tickets added to basket".format(quantity, ticket_type.name))

        # Display buy page
        context = {
            'basket': basket,
            'ticket_types': ticket_types,
            'performance': performance,
            'fringers': fringers,
        }
        return render(request, "tickets/buy.html", context)


class BuyFringerFormHelper(FormHelper):

    form_class = "form-horizontal"
    label_class = "col-xs-12 col-sm-3"
    field_class= "col-xs-12, col-sm-9"
    layout = Layout(
        'type',
        'name', 
        FormActions(
            Submit("action", "Add to Basket")
        ),
    )

class FringersView(LoginRequiredMixin, View):

    def get(self, request):

        # Create fringer formset
        FringerFormSet = modelformset_factory(Fringer, fields = ('name',), extra = 0)
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
            FringerFormSet = modelformset_factory(Fringer, fields = ('name',), extra = 0)
            formset = FringerFormSet(request.POST)

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
            FringerFormSet = modelformset_factory(Fringer, fields = ('name',), extra = 0)
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

    def get(self, request, fringer_id):

        # Get basket and fringer to be removed
        basket = request.user.basket
        fringer = get_object_or_404(Fringer, pk = fringer_id)

        # Delete fringer
        fringer.delete()
        messages.success(request, "Fringer removed from basket")

        # Redisplay checkout
        context = {
            'basket': basket
        }
        return render(request, "tickets/checkout.html", context)


class RemoveTicketView(LoginRequiredMixin, View):

    def get(self, request, ticket_id):

        # Get basket and ticket to be removed
        basket = request.user.basket
        ticket = get_object_or_404(Ticket, pk = ticket_id)

        # Delete ticket
        ticket.delete()
        messages.success(request, "Ticket removed from basket")

        # Redisplay checkout
        context = {
            'basket': basket
        }
        return render(request, "tickets/checkout.html", context)
