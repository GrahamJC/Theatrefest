from django.contrib.auth.models import User
from django.db import models

from catalog.models import Performance


class BoxOffice(models.Model):
	
	name = models.CharField(max_length = 32, unique = True)
	is_online = models.BooleanField(default = False)
	
	def __str__(self):
		return self.name


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
	in_basket = models.DateTimeField(null = True, blank = True)

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
	quantity = models.PositiveIntegerField()
	cost = models.DecimalField(max_digits = 4, decimal_places = 2)
	fringers = models.ManyToManyField(Fringer, related_name = 'tickets')
	in_basket = models.DateTimeField(null = True, blank = True)
	
	def __str__(self):
		return str(quantity) + ' x ' + str(self.performance) + ' (' + self.description + ')' 
