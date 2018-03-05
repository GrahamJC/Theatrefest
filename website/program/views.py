from django.shortcuts import get_object_or_404, render
from django.views import View
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Show, Venue
from .forms import SearchForm

def home(request):
    return render(request, 'program/home.html', {})


def shows(request):
    shows = Show.objects.all()
    context ={
        'shows': shows,
    }
    return render(request, 'program/shows.html', context)

def show_detail(request, show_id):
    show = get_object_or_404(Show, pk = show_id)
    context ={
        'show': show,
    }
    return render(request, 'program/show_detail.html', context)

def venues(request):
    venues = Venue.objects.all()
    context ={
        'venues': venues,
    }
    return render(request, 'program/venues.html', context)

def venue_detail(request, venue_id):
    venue = get_object_or_404(Venue, pk = venue_id)
    context ={
        'venue': venue,
    }
    return render(request, 'program/venue_detail.html', context)


class ShowsView(View):

    def get(self, request):

        # Create the search form and helper
        search = SearchForm(request.GET)
        search_helper = FormHelper()
        search_helper.form_tag = False
        search_helper.label_class = "col-sm-2"
        search_helper.field_class = "col-sm-10"
        search_helper.add_input(Submit('submit', 'Search'))

        # Create context
        context = {
            'search': search,
            'search_helper': search_helper,
        }

        # If valid add search results to context
        if search.is_valid():
            shows = Show.objects
            if search.cleaned_data['days']:
                shows = shows.filter(performances__date__in = search.cleaned_data['days'])
            if search.cleaned_data['venues']:
                shows = shows.filter(venue_id__in = search.cleaned_data['venues'] )
            if search.cleaned_data['genres']:
                shows = shows.filter(genres__id__in = search.cleaned_data['genres'] )
            results = []
            for show in shows.distinct():
                if show.theatrefest_ID:
                    show.details_url = show.theatrefest_ID.format("http:theatrefest.co.uk/18/Companies/{0}.htm")
                else:
                    show_details = reverse("program:show_detail", args = [show.id])
                results.append(show)
            context['results'] = results

        # Render search results
        return render(request, 'program/shows.html', context)

