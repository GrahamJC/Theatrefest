from django import forms

from .models import Venue, Genre, Performance

class SearchForm(forms.Form):

    days = forms.MultipleChoiceField(choices = [], required = False, widget = forms.CheckboxSelectMultiple)
    venues = forms.ModelMultipleChoiceField(Venue.objects.all(), to_field_name = "id", required = False, widget = forms.CheckboxSelectMultiple)
    genres = forms.ModelMultipleChoiceField(Genre.objects.filter(warning = False), to_field_name = "id", required = False, widget = forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        #self.fields['days'].choices = [(date[0], date[0].strftime("%a, %b %d")) for date in Performance.objects.order_by('date').values_list('date').distinct()]
        self.fields['days'].choices = Performance.objects.order_by('date').values_list('date', 'date').distinct()
