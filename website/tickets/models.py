from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models
from decimal import Decimal, ROUND_05UP

from common.models import TimeStampedModel, AutoOneToOneField
from program.models import BoxOffice, Performance


class Sale(TimeStampedModel):

    box_office = models.ForeignKey(BoxOffice, null = True, blank = True, on_delete = models.PROTECT, related_name = 'sales')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.PROTECT, related_name = 'sales')
    customer = models.CharField(max_length = 64, blank = True, default = '')
    buttons = models.IntegerField(blank = True, default = 0)
    amount = models.DecimalField(blank = True, default = 0, max_digits = 5, decimal_places = 2)
    stripe_fee = models.DecimalField(blank = True, default = 0, max_digits = 4, decimal_places = 2)
    completed = models.DateTimeField(null = True, blank = True)

    @property
    def customer_user(self):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email = self.customer)
        except user_model.DoesNotExist:
            user = None
        return user

    @property
    def is_empty(self):
        return (self.buttons == 0) and (self.fringers.count() == 0) and (self.tickets.count() == 0)

    @property
    def button_cost(self):
        return self.buttons * Decimal('1.00')

    @property
    def fringer_cost(self):
        return sum([f.cost for f in self.fringers.all()])

    @property
    def ticket_cost(self):
        return sum([t.cost for t in self.tickets.all()])

    @property
    def total_cost(self):
        return self.button_cost + self.fringer_cost + self.ticket_cost

    @property
    def stripe_charge(self):
        return self.total_cost + self.stripe_fee

    @property
    def performances(self):
        performances = []
        for ticket in self.tickets.values('performance_id').distinct():
            p = Performance.objects.get(pk = ticket['performance_id'])
            tickets = self.tickets.filter(performance_id = ticket['performance_id'])
            performance = {
                'id': p.id,
                'uuid': p.uuid,
                'show': p.show.name,
                'date' : p.date,
                'time': p.time,
                'ticket_cost': sum(t.cost for t in tickets.all()), 
                'tickets': [{'id': t.id, 'uuid': t.uuid, 'description': t.description, 'cost': t.cost} for t in tickets],
            }
            performances.append(performance)
        return performances

    def __str__(self):
        return f'{self.id} ({self.customer})'


class Refund(TimeStampedModel):

    box_office = models.ForeignKey(BoxOffice, null = True, blank = True, on_delete = models.PROTECT, related_name = 'refunds')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.PROTECT, related_name = 'refunds')
    customer = models.CharField(max_length = 64, blank = True, default = '')
    amount = models.DecimalField(blank = True, default = 0, max_digits = 5, decimal_places = 2)
    reason = models.TextField()
    completed = models.DateTimeField(null = True, blank = True)

    @property
    def customer_user(self):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email = self.customer)
        except user_model.DoesNotExist:
            user = None
        return user

    @property
    def is_empty(self):
        return (self.tickets.count() == 0)

    @property
    def ticket_cost(self):
        return sum([t.cost for t in self.tickets.all()])

    @property
    def total_cost(self):
        return self.ticket_cost

    @property
    def performances(self):
        performances = []
        for ticket in self.tickets.values('performance_id').distinct():
            p = Performance.objects.get(pk = ticket['performance_id'])
            tickets = self.tickets.filter(performance_id = ticket['performance_id'])
            performance = {
                'id': p.id,
                'uuid': p.uuid,
                'show': p.show.name,
                'date' : p.date,
                'time': p.time,
                'ticket_cost': sum(t.cost for t in tickets.all()), 
                'tickets': [{'id': t.id, 'uuid': t.uuid, 'description': t.description, 'cost': t.cost} for t in tickets],
            }
            performances.append(performance)
        return performances

    def __str__(self):
        return f'{self.id} ({self.customer})'


class Basket(TimeStampedModel):
    
    user = AutoOneToOneField(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, primary_key = True, related_name = 'basket')

    @property
    def ticket_count(self):
        return self.tickets.count()

    @property
    def has_tickets(self):
        return self.ticket_count > 0

    @property
    def fringer_count(self):
        return self.fringers.count()

    @property
    def has_fringers(self):
        return self.fringer_count > 0

    @property
    def total_count(self):
        return self.ticket_count + self.fringer_count

    @property
    def is_empty(self):
        return self.total_count == 0

    @property
    def ticket_cost(self):
        return sum([t.cost for t in self.tickets.all()])

    @property
    def fringer_cost(self):
        return sum([f.cost for f in self.fringers.all()])

    @property
    def total_cost(self):
        return self.ticket_cost + self.fringer_cost

    @property
    def stripe_charge(self):
        return ((self.total_cost + settings.STRIPE_FEE_FIXED) / (1 - settings.STRIPE_FEE_PERCENT)).quantize(Decimal('.01'), rounding = ROUND_05UP)

    @property
    def stripe_charge_pence(self):
        return int(self.stripe_charge * 100)

    @property
    def stripe_fee(self):
        return self.stripe_charge - self.total_cost

    @property
    def performances(self):
        performances = []
        for t in self.tickets.values('performance_id').distinct():
            p = Performance.objects.get(pk = t['performance_id'])
            tickets = self.tickets.filter(performance = p)
            performance = {
                'id': p.id,
                'show': p.show.name,
                'date' : p.date,
                'time': p.time,
                'ticket_cost': sum(t.cost for t in tickets.filter(performance = p)), 
                'tickets': [{'id': t.id, 'description': t.description, 'cost': t.cost} for t in tickets],
            }
            performances.append(performance)
        return performances

    def __str__(self):
        return self.user.email


class FringerType(TimeStampedModel):

    class Meta:
        ordering = ['name']
    
    name = models.CharField(max_length = 32, unique = True)
    shows = models.PositiveIntegerField(blank = True, default = 0)
    price = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, default = 0)
    is_online = models.BooleanField(default = False)
    rules = models.TextField(blank = True, default = '')
    payment = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, default = 0)

    @property
    def description(self):
        return "{0} shows for £{1:0.2}".format(self.shows, self.price)

    def __str__(self):
        return self.name

class Fringer(TimeStampedModel):

    class Meta:
        ordering = ['user', 'name']
        unique_together = ('user', 'name')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.PROTECT, null = True, blank = True, related_name = 'fringers')
    name = models.CharField(max_length = 32)
    description = models.CharField(max_length = 32)
    shows = models.PositiveIntegerField()
    cost = models.DecimalField(max_digits = 4, decimal_places = 2)
    basket = models.ForeignKey(Basket, on_delete = models.CASCADE, null = True, blank = True, related_name = 'fringers')
    sale = models.ForeignKey(Sale, on_delete = models.CASCADE, null = True, blank = True, related_name = 'fringers')
    payment = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, default = 0)

    @property
    def used(self):
        return self.tickets.filter(refund = None).count()

    @property
    def available(self):
        return self.shows - self.used

    @property
    def valid_tickets(self):
        return self.tickets.exclude(refund__isnull = False)

    def is_available(self, performance = None):
        return (self.available > 0) and ((performance == None) or (performance not in [t.performance for t in self.tickets.filter(refund = None)]))

    def __str__(self):
        if self.user:
            return f"eFringer: {self.user.email} ({self.name})"
        if self.sale:
            return f"Paper: {self.sale.customer}"
        else:
            return f"Fringer({self.id})"

    def get_available(user, performance = None):
        return [f for f in user.fringers.exclude(sale__completed__isnull = True) if f.is_available(performance)]

class TicketType(TimeStampedModel):

    class Meta:
        ordering = ['seqno', 'name']
    
    name = models.CharField(max_length = 32, unique = True)
    seqno = models.IntegerField(default = 1)
    price = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, default = 0)
    is_online = models.BooleanField(default = False)
    is_admin = models.BooleanField(default = False)
    rules = models.TextField(blank = True, default = '')
    payment = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, default = 0)

    @property
    def description(self):
        description = self.name
        if self.price:
            description += f" (£{self.price})"
        return description

    def __str__(self):
        return self.name


class Ticket(TimeStampedModel):

    class Meta:
        ordering = ['performance']

    performance = models.ForeignKey(Performance, on_delete = models.PROTECT, related_name = 'tickets')
    description = models.CharField(max_length = 32)
    cost = models.DecimalField(max_digits = 4, decimal_places = 2)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null = True, on_delete = models.PROTECT, related_name = 'tickets')
    basket = models.ForeignKey(Basket, on_delete = models.CASCADE, null = True, blank = True, related_name = 'tickets')
    fringer = models.ForeignKey(Fringer, on_delete = models.PROTECT, null = True, blank = True, related_name = 'tickets')
    sale = models.ForeignKey(Sale, on_delete = models.CASCADE, null = True, blank = True, related_name = 'tickets')
    refund = models.ForeignKey(Refund, on_delete = models.SET_NULL, null = True, blank = True, related_name = 'tickets')
    payment = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, default = 0)

    @property
    def is_confirmed(self):
        return (self.basket == None) and (self.refund == None)

    @property
    def is_cancelled(self):
        return (self.refund != None)

    def __str__(self):
        return "{0} ({1}): {2}".format(self.id, self.description, self.performance)
