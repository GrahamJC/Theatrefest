from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

"""
class FringerForm(forms.Form):

	def __init__(self, *args, **kwargs):
		fringer_types = kwargs.pop('types')
		super(FringerForm, self).__init__(*args,**kwargs)
		for type in fringer_types:
			self.fields[type.name] = forms.IntegerField(label = '{0} shows for {1}'.format(type.shows, type.price), initial = 0)
			type.form_field = self.fields[type.name]
		self.use_required_attribute = False
		self.helper = FormHelper()
		self.helper.form_class = "form-horizontal"
		self.helper.label_class = "col-sm-3"
		self.helper.field_class = "col-sm-3 col-md-2 col-lg-1"
		self.helper.add_input(Submit('submit', 'Buy'))
"""