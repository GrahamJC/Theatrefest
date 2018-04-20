import os

from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.template import Template, Context
from django.views import View
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Show, Venue, Performance
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

    # Get show
    show = get_object_or_404(Show, pk = show_id)

    # Check for HTML description
    html = None
    if show.html_description:
        context = { 'show': show }
        media_url = getattr(settings, 'MEDIA_URL', '/')
        for image in show.images.all():
            context[f"image_{image.name}_url"] = os.path.join(media_url, image.image.url)
        template = Template(show.html_description)
        html = template.render(Context(context))

    # Render show details
    context ={
        'show': show,
        'html': html,
    }
    return render(request, 'program/show_detail.html', context)

def venues(request):
    venues = Venue.objects.all()
    context = {
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


class ScheduleView(View):

    def get(self, request):

        # Generate the schedule
        #pages = []
        #for date_dict in Performance.objects.order_by('date').values('date').distinct():
        #    date = date_dict["date"]
        #    venues = []
        #    for venue_dict in Show.objects.filter(performances__date = date).order_by().values('venue_id').distinct():
        #        venue = Venue.objects.get(pk = venue_dict["venue_id"])
        #        venues.append({
        #            'name': venue.name,
        #        })
        #    pages.append({
        #        'date': date,
        #        'venues': venues,
        #    })

        # Build the schedule
        days = []
        day = None
        for performance in Performance.objects.order_by('date', 'show__venue__name', 'time').values('date', 'show__venue__name', 'time', 'show__name'):
            
            # If the date has changed start a new day
            if day and performance['date'] != day['date']:
                days.append(day)
                day = None
            if not day:
                day = {
                    'date': performance['date'],
                    'venues': [],
                }
                venue = None

            # If the venue has changed add it to the page and start a new one
            if venue and performance['show__venue__name'] != venue['name']:
                day['venues'].append(venue)
                venue = None
            if not venue:
                venue = {
                    'name': performance['show__venue__name'],
                    'performances': [],
                }

            # Add performance to venue
            venue['performances'].append(
                {
                    'show': performance['show__name'],
                    'time': performance['time'],
                }
            )

        # Add final day and venue
        if day:
            if venue:
                day['venues'].append(venue)
            days.append(day)

        # Render schedule
        context = {
            'days': days,
        }
        return render(request, 'program/schedule.html', context)


