from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from .models import BoxOffice, Basket, FringerType, Fringer


class BuyView(LoginRequiredMixin, View):

    def get(self, request, performance_id):
        performance = get_object_or_404(Performance, pk = performance_id)
        return HttpResponse("Buy tickets for: " + performance.show.name + " at " + str(performance.date_time))


class FringersView(LoginRequiredMixin, View):

    def get(self, request):
        context = {
            'fringer_types': FringerType.objects.filter(is_online = True),
            'fringers': Fringer.objects.filter(user = request.user, basket = None),
        }
        return render(request, "tickets/fringers.html", context)

    def post(self, request):
        fringer_type = get_object_or_404(FringerType, name = request.POST.get("add_to_basket"))
        box_office = BoxOffice.objects.get(name = 'Online')
        #basket = request.user.basket
        basket, created = Basket.objects.get_or_create(user = request.user)
        fringer = Fringer(
            user = request.user,
            box_office = box_office,
            date_time = datetime.now(),
            description = fringer_type.name,
            shows = fringer_type.shows,
            cost = fringer_type.price,
            basket = basket
        )
        fringer.save()
        basket.updated = datetime.now()
        basket.save()
        return redirect(reverse('tickets:basket'))

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


class BasketView(LoginRequiredMixin, View):

    def get(self, request):
        basket, created = Basket.objects.get_or_create(user = request.user)
        context = {
            'basket': basket,
        }
        return render(request, "tickets/basket.html", context)

    def post(self, request):
        basket, created = Basket.objects.get_or_create(user = request.user)
        context = {
            'basket': basket,
        }
        return render(request, "tickets/basket.html", context)
