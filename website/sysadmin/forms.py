from django import forms


class EMailForm(forms.Form):

    from_email = forms.EmailField(required=True)
    to_email = forms.EmailField(required=True)
    subject = forms.CharField(required=True, max_length=128)
    body = forms.CharField(required=True, max_length=1024, widget=forms.Textarea)
