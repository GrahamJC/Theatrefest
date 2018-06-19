from django import forms

from accounts.models import User


class VolunteerForm(forms.Form):

    user = forms.ModelChoiceField(queryset = None, required = True, empty_label = 'Select user to become a volunteer')
    first_name = forms.CharField(required = True, max_length = 32)
    last_name = forms.CharField(required = True, max_length = 32)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(is_volunteer = False, is_admin = False).order_by('email')


class EMailForm(forms.Form):

    from_email = forms.EmailField(required=True)
    to_email = forms.EmailField(required=True)
    subject = forms.CharField(required=True, max_length=128)
    body = forms.CharField(required=True, max_length=1024, widget=forms.Textarea)
