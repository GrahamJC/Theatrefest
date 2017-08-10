from django.views import View
from django.shortcuts import render

from registration.backends.simple.views import RegistrationView

from .forms import MyRegistrationForm

class MyRegistrationView(RegistrationView):
	
	form_class = MyRegistrationForm
	
	def get_success_url(self, user):
		return "/accounts/profile"
		

class ProfileView(View):

	template_name = "accounts/profile.html"
	
	def get(self, request):
		return render(request, self.template_name, {})
		
	def post(self, request, *args, **kwargs):
		return render(request, self.template_name, {})
		
