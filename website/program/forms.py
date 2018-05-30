from django import forms

from .models import Venue, Genre, Performance

class SearchForm(forms.Form):

    # Search by day
    days = forms.MultipleChoiceField(choices = Performance.objects.order_by('date').values_list('date', 'date').distinct(), required = False, widget = forms.CheckboxSelectMultiple)

    # Search by ticketed venue with option to include non-ticketed
    venue_list = [(v.id, v.name) for v in Venue.objects.filter(is_searchable = True)]
    venue_list.append((0, 'Alt Spaces'))
    venues = forms.MultipleChoiceField(choices = venue_list, required = False, widget = forms.CheckboxSelectMultiple)

    # Search by genre
    genres = forms.ModelMultipleChoiceField(Genre.objects.all(), to_field_name = "id", required = False, widget = forms.CheckboxSelectMultiple)
