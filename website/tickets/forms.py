from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from crispy_forms.bootstrap import FormActions, StrictButton

class FringerForm(forms.Form):

    def __init__(self, fringer_types, *args, **kwargs):

        #Call base constructor
        super(FringerForm, self).__init__(*args, **kwargs)

        # Create fringer type choices
        fringer_choices = [('', '')]
        for fringer_type in fringer_types:
            fringer_choices.append((fringer_type.id, fringer_type.name))

        # Add fields
        self.fields['type'] = forms.ChoiceField(label = "Type", choices = fringer_choices)
        self.fields['name'] = forms.CharField(label = "Name", max_length = 32) 
        self.use_required_attribute = False
        helper = FormHelper()
        helper.form_class = "form-inline"
        helper.field_template = 'bootstrap3/layout/inline_field.html'
        helper.layout = Layout(
            'type',
            'name',
            FormActions(Submit('action','Add to Basket')),
        )
        self.helper = helper