from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from website.utils import init_alerts
from catalog.models import Performance
from .models import BoxOffice, Basket, FringerType, Fringer, TicketType, Ticket


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
        alerts = init_alerts()

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
                    alerts['success'].append("Ticket purchased with fringer {0}".format(fringer.name))

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
                    alerts['success'].append("{0} x {1} tickets added to basket".format(quantity, ticket_type.name))

        # Display buy page
        context = {
            'basket': basket,
            'ticket_types': ticket_types,
            'performance': performance,
            'fringers': fringers,
            'alerts': alerts,
        }
        return render(request, "tickets/buy.html", context)


class FringersView(LoginRequiredMixin, View):

    def get(self, request):
        context = {
            'fringer_types': FringerType.objects.filter(is_online = True),
            'fringers': Fringer.objects.filter(user = request.user, basket = None),
            'basket': request.user.basket,
        }
        return render(request, "tickets/fringers.html", context)

    def post(self, request):

        # Get the action and basket
        action = request.POST.get("action")
        basket = request.user.basket
        alerts = init_alerts()

        # Check for add to basket
        if action == "add":

            # Get fringer type, box office and basket
            fringer_type = get_object_or_404(FringerType, name = request.POST.get("fringer_type"))
            name = request.POST.get("name")
            box_office = get_object_or_404(BoxOffice, name = 'Online')

            # Create new fringer and add to basket
            fringer = Fringer(
                user = request.user,
                name = name,
                box_office = box_office,
                date_time = datetime.now(),
                description = fringer_type.name,
                shows = fringer_type.shows,
                cost = fringer_type.price,
            )
            fringer.save()
            if not name:
                fringer.name = "Fringer{0}".format(fringer.id)
                fringer.save()
            basket.add_item(fringer)
            alerts['success'].append("{0} added to basket".format(fringer_type))

        else: # Must be rename

            # Get the fringer id
            fringer_id = int(action[6:])
            fringer = get_object_or_404(Fringer, pk = fringer_id)
            new_name = request.POST.get("fringer_name{0}".format(fringer_id))
            if new_name:
                old_name = fringer.name
                fringer.name = new_name
                fringer.save()
                alerts['success'].append("{0} renamed to {1}".format(old_name, new_name))

        # Redisplay with confirmation
        context = {
            'fringer_types': FringerType.objects.filter(is_online = True),
            'fringers': Fringer.objects.filter(user = request.user, basket = None),
            'alerts': alerts,
            'basket': basket,
        }
        return render(request, "tickets/fringers.html", context)

"""
from .forms import FringerForm

class FringersView(View):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FringersView, self).dispatch(*args, **kwargs)
            
    def get(self, request):
        fringer_types = FringerType.objects.filter(is_online = True)
        form = FringerForm(types = fringer_types)
        context = {
            'form': form,
        }
        return render(request, "tickets/fringers.html", context)

    def post(self, request):
        box_office = BoxOffice.objects.get(name = 'Online')
        fringer_types = FringerType.objects.filter(is_online = True)
        form = FringerForm(request.POST, types = fringer_types)
        if form.is_valid():
            response = ''
            for type in fringer_types:
                quantity = form.cleaned_data[type.name]
                for i in range(0, quantity):
                    fringer = Fringer(
                        user = request.user,
                        box_office = box_office,
                        date_time = datetime.now(),
                        description = type.name,
                        shows = type.shows,
                        cost = type.price,
                        in_basket = None
                    )
                    fringer.save()
        context = {
            'form': form,
        }
        return render(request, "tickets/fringers.html", context)
"""


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
        alerts = init_alerts()

        # Complete purchase of fringers (i.e. remove them from the basket)
        for fringer in basket.fringers.all():
            fringer.basket = None
            fringer.save()
            alerts['success'].append("Purchase complete: {0}".format(fringer.description))

        # Complete purchase of tickets (i.e. remove them from the basket)
        for ticket in basket.tickets.all():
            ticket.basket = None
            ticket.save()
            alerts['success'].append("Purchase complete: {0}".format(ticket))

        # Redisplay empty basket and purchase confirmation
        context = {
            'alerts': alerts,
            'basket': basket,
        }
        return render(request, "tickets/checkout.html", context)


class RemoveFringerView(LoginRequiredMixin, View):

    def get(self, request, fringer_id):

        # Get basket and fringer to be removed
        basket = request.user.basket
        fringer = get_object_or_404(Fringer, pk = fringer_id)
        alerts = init_alerts()

        # Delete fringer
        fringer.delete()
        alerts['success'].append("Fringer removed from basket")

        # Redisplay checkout
        context = {
            'alerts': alerts,
            'basket': basket
        }
        return render(request, "tickets/checkout.html", context)


class RemoveTicketView(LoginRequiredMixin, View):

    def get(self, request, ticket_id):

        # Get basket and ticket to be removed
        basket = request.user.basket
        ticket = get_object_or_404(Ticket, pk = ticket_id)
        alerts = init_alerts()

        # Delete ticket
        ticket.delete()
        alerts['success'].append("Ticket removed from basket")

        # Redisplay checkout
        context = {
            'alerts': alerts,
            'basket': basket
        }
        return render(request, "tickets/checkout.html", context)
