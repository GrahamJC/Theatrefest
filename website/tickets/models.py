from datetime import datetime
from django.contrib.auth.models import User
from django.db import models

from website.utils import AutoOneToOneField
from catalog.models import Performance


class BoxOffice(models.Model):
    
    name = models.CharField(max_length = 32, unique = True)
    is_online = models.BooleanField(default = False)
    
    def __str__(self):
        return self.name


class Basket(models.Model):
    
    user = AutoOneToOneField(User, on_delete = models.CASCADE, primary_key = True, related_name = 'basket')
    created = models.DateTimeField(default = datetime.now())
    updated = models.DateTimeField(default = datetime.now())

    @property
    def has_fringers(self):
        return self.fringers.count > 0

    @property
    def has_tickets(self):
        return self.fringers.count > 0

    @property
    def is_empty(self):
        return not self.has_fringers and not self.has_tickets

    def add_item(self, item):
        item.basket = self
        item.save()
        self.updated = datetime.now()
        self.save()

    def remove_item(self, item):
        if item.basket == self:
            item.basket = None
            item.save()

    def __str__(self):
        return self.user.username


class FringerType(models.Model):
    
    name = models.CharField(max_length = 32, unique = True)
    shows = models.PositiveIntegerField(blank = True, default = 0)
    price = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, default = 0)
    is_online = models.BooleanField(default = False)
    rules = models.TextField(blank = True, default = '')

    def description(self):
        return "{0} for £{1:0.2}".format(self.shows, self.price)

    def __str__(self):
        return self.name

class Fringer(models.Model):
    
    user = models.ForeignKey(User, on_delete = models.PROTECT, related_name = 'fringers')
    name = models.CharField(max_length = 32, blank = True, default = '')
    box_office = models.ForeignKey(BoxOffice, on_delete = models.PROTECT, related_name = 'fringers')
    date_time = models.DateTimeField()
    description = models.CharField(max_length = 32)
    shows = models.PositiveIntegerField()
    cost = models.DecimalField(max_digits = 4, decimal_places = 2)
    basket = models.ForeignKey(Basket, on_delete = models.CASCADE, null = True, blank = True, related_name = 'fringers')

    @property
    def used(self):
        return self.tickets.count()

    @property
    def unused(self):
        return self.shows - self.used

    @property
    def has_unused(self):
        return self.unused > 0

    def __str__(self):
        return "{0}:{1}".format(self.user.username, self.name)


class TicketType(models.Model):
    
    name = models.CharField(max_length = 32, unique = True)
    price = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, default = 0)
    fringers = models.PositiveIntegerField(blank = True, default = 0)
    is_online = models.BooleanField(default = False)
    rules = models.TextField(blank = True, default = '')

    def __str__(self):
        return self.name


class Ticket(models.Model):

    user = models.ForeignKey(User, on_delete = models.PROTECT, related_name = 'tickets')
    performance = models.ForeignKey(Performance, on_delete = models.PROTECT, related_name = 'tickets')
    box_office = models.ForeignKey(BoxOffice, on_delete = models.PROTECT, related_name = 'tickets')
    date_time = models.DateTimeField()
    description = models.CharField(max_length = 32)
    cost = models.DecimalField(max_digits = 4, decimal_places = 2)
    fringer = models.ForeignKey(Fringer, on_delete = models.PROTECT, null = True, blank = True, related_name = 'tickets')
    basket = models.ForeignKey(Basket, on_delete = models.CASCADE, null = True, blank = True, related_name = 'tickets')
    
    def __str__(self):
        return "{0}:{1}:{2}".format(self.user.username, self.description, self.performance)
