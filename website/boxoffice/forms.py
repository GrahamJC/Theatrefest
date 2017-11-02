from django import forms

from catalog.models import Show, Performance

class TicketsForm( forms.Form ):

    show = forms.ModelChoiceField( Show.objects.all(), label = "Show" )
    performance_id = forms.IntegerField( label = "Performance", widget = forms.HiddenInput() )

