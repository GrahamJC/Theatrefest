from django import forms

from program.models import Show, Performance
from tickets.models import Fringer

class CustomerForm(forms.Form):

    customer = forms.CharField(label = 'Customer', required = True, max_length = 64)
    customer.widget.attrs['placeholder'] = '-- Enter customer name or e-mail --'


class SaleTicketsForm(forms.Form):

    show = forms.ModelChoiceField(Show.objects.none(), to_field_name = 'uuid', label = "Show", empty_label = '-- Select show --')
    performance = forms.ModelChoiceField(Performance.objects.none(), to_field_name = 'uuid', label = "Performance", empty_label = '-- Select performance --')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['show'].queryset = Show.objects.filter(is_cancelled = False, venue__is_ticketed = True)
        self.fields['performance'].queryset = Performance.objects.none()
        if 'show' in self.data:
            try:
                show_uuid = self.data.get('show')
                self.fields['performance'].queryset = Performance.objects.filter(show__uuid = show_uuid)
            except:
                pass


class SaleTicketSubForm(forms.Form):

    type_id = forms.IntegerField(widget = forms.HiddenInput())
    name = forms.CharField(widget = forms.HiddenInput())
    price = forms.DecimalField(widget = forms.HiddenInput())
    quantity = forms.IntegerField(required = False, min_value = 0)

    def clean_quantity(self):
        value = self.cleaned_data['quantity']
        return value or 0


class SaleFringerSubForm(forms.Form):

    performance = None
    fringer_id = forms.IntegerField(widget = forms.HiddenInput())
    name = forms.CharField(widget = forms.HiddenInput())
    buy = forms.BooleanField(required = False)

    def clean_buy(self):
        buy = self.cleaned_data['buy']
        if buy:
            try:
                fringer = Fringer.objects.get(pk = self.cleaned_data['fringer_id'])
                if not fringer.is_available(self.performance):
                    raise forms.ValidationError('Already used for this performance')
            except Fringer.DoesNotExist:
                raise forms.ValidationError('Not found')
        return buy


class SaleExtrasForm(forms.Form):

    buttons = forms.IntegerField(label = 'Buttons', required = False, min_value = 0)
    fringers = forms.IntegerField(label = 'Paper fringers', required = False, min_value = 0)

    def clean_buttons(self):
        value = self.cleaned_data['buttons']
        return value or 0

    def clean_fringers(self):
        value = self.cleaned_data['fringers']
        return value or 0


class RefundTicketForm(forms.Form):

    ticket_no = forms.IntegerField(label = 'Number')


class RefundForm(forms.Form):

    amount = forms.DecimalField(label = 'Refund', min_value = 0, max_digits = 5, decimal_places = 2)
    reason = forms.CharField(label = 'Reason', widget = forms.Textarea())
