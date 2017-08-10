from django.shortcuts import get_object_or_404, render

from .models import Show, Venue

def home(request):
	return render(request, 'catalog/home.html', {})

def shows(request):
	shows = Show.objects.all()
	context ={
		'shows': shows,
	}
	return render(request, 'catalog/shows.html', context)

def show_detail(request, show_id):
	show = get_object_or_404(Show, pk = show_id)
	context ={
		'show': show,
	}
	return render(request, 'catalog/show_detail.html', context)

def venues(request):
	venues = Venue.objects.all()
	context ={
		'venues': venues,
	}
	return render(request, 'catalog/venues.html', context)

def venue_detail(request, venue_id):
	venue = get_object_or_404(Venue, pk = venue_id)
	context ={
		'venue': venue,
	}
	return render(request, 'catalog/venue_detail.html', context)
