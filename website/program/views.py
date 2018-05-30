import os

from django.db.models import Q
from django.db.models.functions import Lower
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.template import Template, Context
from django.views import View
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Show, Venue, Performance
from .forms import SearchForm

def home(request):
    return render(request, 'program/home.html', {})


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
                if '0' in search.cleaned_data['venues']:
                    shows = shows.filter(Q(venue_id__in = search.cleaned_data['venues']) | Q(venue__is_ticketed = False))
                else:
                    shows = shows.filter(venue_id__in = search.cleaned_data['venues'])
            if search.cleaned_data['genres']:
                shows = shows.filter(genres__id__in = search.cleaned_data['genres'] )
            shows = shows.order_by(Lower('name'))
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


class ShowDetailView(View):

    def get(self, request, show_id):

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


class ScheduleView(View):

    def _add_non_scheduled_performances(self, day):
        performances = []
        for performance in Performance.objects.filter(show__venue__is_scheduled = False, date = day['date']).order_by('time').values('time', 'show__id', 'show__name', 'show__is_cancelled'):
            performances.append(
                {
                    'show_id': performance['show__id'],
                    'show_name': performance['show__name'],
                    'time': performance['time'],
                    'is_cancelled': performance['show__is_cancelled'],
                }
            )
        day['venues'].append(
            {
                'name': 'Other (alt spaces)',
                'color': '',
                'performances': performances,
            }
        )

    def get(self, request):

        # Build the schedule
        days = []
        day = None
        for performance in Performance.objects.filter(show__venue__is_scheduled = True).order_by('date', 'show__venue__map_index', 'show__venue__name', 'time').values('date', 'show__venue__name', 'show__venue__color', 'time', 'show__id', 'show__name', 'show__is_cancelled'):
            
            # If the date has changed start a new day
            if day and performance['date'] != day['date']:
                if venue:
                    day['venues'].append(venue)
                    venue = None
                self._add_non_scheduled_performances(day)
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
                    'color': performance['show__venue__color'],
                    'performances': [],
                }

            # Add performance to venue
            venue['performances'].append(
                {
                    'show_id': performance['show__id'],
                    'show_name': performance['show__name'],
                    'time': performance['time'],
                    'is_cancelled': performance['show__is_cancelled'],
                }
            )

        # Add final day and venue
        if day:
            if venue:
                day['venues'].append(venue)
            self._add_non_scheduled_performances(day)
            days.append(day)

        # Render schedule
        context = {
            'days': days,
        }
        return render(request, 'program/schedule.html', context)


class VenuesView(View):

    def get(self, request):

        # List ticketd and non-ticketd vebues separately
        context = {
            'ticketed_venues': Venue.objects.filter(is_ticketed = True).order_by('map_index', 'name'),
            'nonticketed_venues': Venue.objects.filter(is_ticketed = False).order_by('map_index', 'name'),
        }

        # Render venue list
        return render(request, 'program/venues.html', context)


class VenueDetailView(View):

    def get(self, request, venue_id):

        venue = get_object_or_404(Venue, pk = venue_id)
        context = {
            'venue': venue,
            'shows': venue.shows.order_by(Lower('name')),
        }
        return render(request, 'program/venue_detail.html', context)


class TheatrefestView(View):

    def get(self, request, name):
        urls = {
            'home': r'http://theatrefest.co.uk/index.htm',
            'tickets': r'http://theatrefest.co.uk/18/booking.htm',
            'performers': r'http://theatrefest.co.uk/performers.htm',
            'volunteers': r'http://theatrefest.co.uk/volunteers.htm',
            'contacts': r'http://theatrefest.co.uk/contacts.htm',
        }
        return redirect(urls[name])


from django.http import HttpResponse

from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4, portrait, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors

class SchedulePdfView(View):

    def get(self, request):

        # Create a Platypus story
        response = HttpResponse(content_type = 'application/pdf')
        response["Content-Disposition"] = 'inline; filename="TheatrefestSchedule.pdf"'
        doc = SimpleDocTemplate(
            response,
            pagesize = landscape(A4),
            leftMargin = 0.5*cm,
            rightMargin = 0.5*cm,
            topMargin = 0.5*cm,
            bottomMargin = 0.5*cm,
        )
        styles = getSampleStyleSheet()
        story = []

        # Table data and styles
        table_data = []
        table_styles = []

        # Paragraph styles
        venue_style = ParagraphStyle(
            name = 'Venue',
            align = TA_CENTER,
            fontSize = 10,
            textColor = colors.white,
        )
        day_style = ParagraphStyle(
            name = 'Day',
            fontSize = 10,
        )
        time_style = ParagraphStyle(
            name = 'Time',
            fontSize = 8,
            leading = 8,
            textColor = colors.indianred,
        )
        show_style = ParagraphStyle(
            name = 'Show',
            fontSize = 8,
            leading = 8,
            textColor = '#1a7cf3',
        )

        # Venues
        venues = Venue.objects.filter(is_scheduled = True).order_by('map_index')
        venues_data = []
        for v in venues:
            venues_data.append(Paragraph(f'<para align="center"><b>{v.name}</b></para>', venue_style))
            venues_data.append('')
        table_data.append(venues_data)
        for i, v in enumerate(venues):
            table_styles.append(('SPAN', (2*i, 0), (2*i + 1, 0)))
            table_styles.append(('BACKGROUND', (2*i, 0), (2*i + 1, 0), v.color ))

        # Days
        days = Performance.objects.filter(show__is_cancelled = False, show__venue__is_scheduled = True).order_by('date').values('date').distinct()
        day_color = ('#fbe4d5', '#fff2cc', '#e2efd9', '#deeaf6')
        for index, day in enumerate(days):

            # Add a row for the day
            first_row = len(table_data)
            table_data.append([Paragraph(f"{day['date']:%A %d}", day_style)] + ['' for i in range(2*len(venues) - 1)])
            table_styles.append(('SPAN', (0, first_row), (-1, first_row)))

            # Get performances for each venue
            venue_performances = [ Performance.objects.filter(show__is_cancelled = False, show__venue = v, date = day['date']).order_by('time') for v in venues]
            slots = max([len(vp) for vp in venue_performances])
            for i in range(slots):
                slot_data = []
                for v in range(len(venues)):
                    if (i < len(venue_performances[v])):
                        performance = venue_performances[v][i]
                        slot_data.append(Paragraph(f'{performance.time:%I:%M}', time_style))
                        slot_url = f'http://{ request.get_host() }{ reverse("program:show_detail", args = [performance.show.id]) }' 
                        slot_data.append(Paragraph(f'<a href="{ slot_url }">{ performance.show.name }</a>', show_style))
                    else:
                        slot_data.append('')
                        slot_data.append('')
                table_data.append(slot_data)

            # Set background color
            table_styles.append(('BACKGROUND', (0, first_row), (-1, len(table_data)), day_color[index % len(day_color)]))
            for i in range(len(venues) - 1):
                table_styles.append(('LINEAFTER', (2*i + 1, first_row + 1), (2*i + 1, len(table_data)), 1, colors.gray))

        # Table styles
        table_styles.append(('VALIGN', (0, 0), (-1, -1), 'TOP'))
        table_styles.append(('ALIGN', (0, 0), (-1, 0), 'CENTER'))
        table_styles.append(('LEFTPADDING', (0, 0), (-1, -1), 2))
        table_styles.append(('RIGHTPADDING', (0, 0), (-1, -1), 2))
        table_styles.append(('TOPPADDING', (0, 0), (-1, -1), 1))
        table_styles.append(('BOTTOMPADDING', (0, 0), (-1, -1), 2))
        table_styles.append(('BOX', (0, 0), (-1, -1), 2, colors.gray))
        table_styles.append(('GRID', (0, 0), (-1, 0), 1, colors.gray))
        table_styles.append(('LINEBELOW', (0, 1), (-1, -1), 0.25, colors.gray))

        slot_width_cm = 28.3 / len(venues)
        time_width_cm = 0.9
        show_width_cm = slot_width_cm - time_width_cm
        table = Table(
            table_data,
            colWidths = len(venues) * [time_width_cm*cm, show_width_cm*cm],
            hAlign = 'LEFT',
            vAlign = 'TOP',
            style = table_styles,
        )
        story.append(table)

        # Create PDF document and return it
        doc.build(story)
        return response
