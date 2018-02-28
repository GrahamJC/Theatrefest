from django import forms

from .models import Venue, Genre, Performance

class SearchForm(forms.Form):

    days_choices = [(date[0], date[0].strftime("%a, %b %d")) for date in Performance.objects.order_by('date').values_list('date').distinct()]
    days = forms.MultipleChoiceField(choices = days_choices, required = False, widget = forms.CheckboxSelectMultiple)
    venues = forms.MultipleChoiceField(choices = [(venue.id, venue.name) for venue in Venue.objects.all()], required = False, widget = forms.CheckboxSelectMultiple)
    genres = forms.MultipleChoiceField(choices = [(genre.id, genre.name) for genre in Genre.objects.all() if not genre.warning], required = False, widget = forms.CheckboxSelectMultiple)
