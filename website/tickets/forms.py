from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from crispy_forms.bootstrap import FormActions, StrictButton

from .models import Fringer


class BuyFringerForm(forms.Form):

    def __init__(self, fringer_types, *args, **kwargs):

        #Call base constructor
        super(BuyFringerForm, self).__init__(*args, **kwargs)

        # Create fringer type choices
        fringer_choices = [(t.id, "{0} shows for £{1:0.2}".format(t.shows, t.price)) for t in fringer_types]

        # Add fields
        self.fields['type'] = forms.ChoiceField(label = "Type", choices = fringer_choices, initial = [fringer_choices[0][0]])
        self.fields['name'] = forms.CharField(label = "Name", max_length = 32)

