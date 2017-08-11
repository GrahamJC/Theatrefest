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
    
    def __str__(self):
        return self.user.username

    def is_empty(self):
        return not(self.fringers.all() or self.tickets.all())

    def add_item(self, item):
        item.basket = self
        item.save()
        self.updated = datetime.now()
        self.save()


class FringerType(models.Model):
    
    name = models.CharField(max_length = 32, unique = True)
    shows = models.PositiveIntegerField(blank = True, default = 0)
    price = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, default = 0)
    is_online = models.BooleanField(default = False)
    rules = models.TextField(blank = True, default = '')

    def __str__(self):
        return self.name


class Fringer(models.Model):
    
    user = models.ForeignKey(User, on_delete = models.PROTECT, related_name = 'fringers')
    box_office = models.ForeignKey(BoxOffice, on_delete = models.PROTECT, related_name = 'fringers')
    date_time = models.DateTimeField()
    description = models.CharField(max_length = 32)
    shows = models.PositiveIntegerField()
    cost = models.DecimalField(max_digits = 4, decimal_places = 2)
    basket = models.ForeignKey(Basket, on_delete = models.CASCADE, null = True, blank = True, related_name = 'fringers')

    def __str__(self):
        return self.description + ' (' + self.user.username + ')'


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
        return str(self.performance) + ': ' + self.perfromance
