from django import forms

from program.models import Show, Performance

class TicketsForm(forms.Form):

    show_id = forms.ModelChoiceField(Show.objects.filter(venue__is_ticketed = True), label = "Show", empty_label = '-- Select show --')
    performance_id = forms.IntegerField(label = "Performance", widget = forms.Select(choices = (('', '-- Select performance --'),)))


class TicketSubForm(forms.Form):

    type_id = forms.IntegerField(widget = forms.HiddenInput())
    name = forms.CharField(widget = forms.HiddenInput())
    price = forms.DecimalField(widget = forms.HiddenInput())
    quantity = forms.IntegerField(required = False, min_value = 0)

    def clean_quantity(self):
        value = self.cleaned_data['quantity']
        return value or 0


class ExtrasForm(forms.Form):

    buttons = forms.IntegerField(required = False, min_value = 0)
    fringers = forms.IntegerField(required = False, min_value = 0)

    def clean_buttons(self):
        value = self.cleaned_data['buttons']
        return value or 0

    def clean_fringers(self):
        value = self.cleaned_data['fringers']
        return value or 0


class SaleForm(forms.Form):

    customer = forms.CharField(max_length = 64, widget = forms.TextInput(attrs = {'placeholder': '-- Enter customer e-mail or name --'}))


