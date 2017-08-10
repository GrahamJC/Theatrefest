from django.contrib.auth.forms import AuthenticationForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from registration.forms import RegistrationForm

class MyAuthenticationForm(AuthenticationForm):

	def __init__(self, *args, **kwargs):
		super(MyAuthenticationForm, self).__init__(*args,**kwargs)
		self.use_required_attribute = False
		self.helper = FormHelper()
		self.helper.form_class = "form-horizontal"
		self.helper.label_class = "col-sm-2"
		self.helper.field_class = "col-sm-10"
		self.helper.add_input(Submit('submit', 'Login'))


class MyRegistrationForm(RegistrationForm):

	def __init__(self, *args, **kwargs):
		super(MyRegistrationForm, self).__init__(*args,**kwargs)
		self.use_required_attribute = False
		self.helper = FormHelper()
		self.helper.form_class = "form-horizontal"
		self.helper.label_class = "col-sm-2"
		self.helper.field_class = "col-sm-10"
		self.helper.add_input(Submit('submit', 'Register'))
