from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render
from django.views import View

from .forms import EMailForm

class EMailView(View):

    def get(self, request):
        form = EMailForm(initial={'from_email': settings.DEFAULT_FROM_EMAIL, 'to_email': 'graham.cockell@outlook.com', 'subject': 'Test', 'body': 'Hello world!'})
        return render(request, "sysadmin/email.html", { 'form': form })


    def post(self, request):
        form = EMailForm(request.POST)
        if form.is_valid():
            send_mail(form.cleaned_data['subject'], form.cleaned_data['body'], form.cleaned_data['from_email'], [form.cleaned_data['to_email']])
            form = EMailForm(initial={'from_email': settings.DEFAULT_FROM_EMAIL, 'to_email': 'graham.cockell@outlook.com', 'subject': 'Test', 'body': 'Hello world!'})
        return render(request, "sysadmin/email.html", { 'form': form })



