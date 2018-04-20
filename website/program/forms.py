from django import forms

from .models import Venue, Genre, Performance

class SearchForm(forms.Form):

    days = forms.MultipleChoiceField(choices = [], required = False, widget = forms.CheckboxSelectMultiple)
    venues = forms.ModelMultipleChoiceField(Venue.objects.all(), to_field_name = "id", required = False, widget = forms.CheckboxSelectMultiple)
    genres = forms.ModelMultipleChoiceField(Genre.objects.all(), to_field_name = "id", required = False, widget = forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['days'].choices = Performance.objects.order_by('date').values_list('date', 'date').distinct()
