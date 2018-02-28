from django.db import models

from common.models import TimeStampedModel


class BoxOffice(TimeStampedModel):

    class Meta:
        ordering = ['name']
    
    name = models.CharField(max_length = 32, unique = True)
    
    def __str__(self):
        return self.name


class Venue(TimeStampedModel):

    class Meta:
        ordering = ['name']

    name = models.CharField(max_length = 128, unique = True)
    image = models.ImageField(upload_to = 'uploads/program/venue/', blank = True, default = '')
    description = models.TextField(blank = True, default = '')
    capacity = models.IntegerField(null = True, blank = True)
    color = models.CharField(max_length = 16, blank = True, default = '')
    address1 = models.CharField(max_length = 64, blank = True, default = '')
    address2 = models.CharField(max_length = 64, blank = True, default = '')
    city = models.CharField(max_length = 32, blank = True, default = '')
    post_code = models.CharField(max_length = 10, blank = True, default = '')
    telno = models.CharField(max_length = 32, blank = True, default = '')
    email = models.EmailField(max_length = 128, blank = True, default = '')
    website = models.URLField(max_length = 128, blank = True, default = '')
    facebook = models.CharField(max_length = 64, blank = True, default = '')
    twitter = models.CharField(max_length = 64, blank = True, default = '')
    instagram = models.CharField(max_length = 64, blank = True, default = '')
    primary_contact = models.CharField(max_length = 64, blank = True, default = '')
    primary_telno = models.CharField(max_length = 32, blank = True, default = '')
    primary_mobile = models.CharField(max_length = 32, blank = True, default = '')
    primary_email = models.EmailField(max_length = 64, blank = True, default = '')
    secondary_contact = models.CharField(max_length = 64, blank = True, default = '')
    secondary_telno = models.CharField(max_length = 32, blank = True, default = '')
    secondary_mobile = models.CharField(max_length = 32, blank = True, default = '')
    secondary_email = models.EmailField(max_length = 64, blank = True, default = '')
    box_office = models.ForeignKey(BoxOffice, null = True, blank = True, on_delete = models.SET_NULL, related_name = 'venues')

    def __str__(self):
        return self.name


class Company(TimeStampedModel):

    class Meta:
        ordering = ['name']

    name = models.CharField(max_length = 128, unique = True)
    image = models.ImageField(upload_to = 'uploads/program/company/', blank = True, default = '')
    description = models.TextField(blank = True, default = '')
    address1 = models.CharField(max_length = 64, blank = True, default = '')
    address2 = models.CharField(max_length = 64, blank = True, default = '')
    city = models.CharField(max_length = 32, blank = True, default = '')
    post_code = models.CharField(max_length = 10, blank = True, default = '')
    telno = models.CharField(max_length = 32, blank = True, default = '')
    email = models.EmailField(max_length = 128, blank = True, default = '')
    website = models.URLField(max_length = 128, blank = True, default = '')
    facebook = models.CharField(max_length = 64, blank = True, default = '')
    twitter = models.CharField(max_length = 64, blank = True, default = '')
    instagram = models.CharField(max_length = 64, blank = True, default = '')
    primary_contact = models.CharField(max_length = 64, blank = True, default = '')
    primary_telno = models.CharField(max_length = 32, blank = True, default = '')
    primary_mobile = models.CharField(max_length = 32, blank = True, default = '')
    primary_email = models.EmailField(max_length = 64, blank = True, default = '')
    secondary_contact = models.CharField(max_length = 64, blank = True, default = '')
    secondary_telno = models.CharField(max_length = 32, blank = True, default = '')
    secondary_mobile = models.CharField(max_length = 32, blank = True, default = '')
    secondary_email = models.EmailField(max_length = 64, blank = True, default = '')

    def __str__(self):
        return self.name


class Genre(TimeStampedModel):

    class Meta:
        ordering = ['name']

    name = models.CharField(max_length = 32, unique = True)
    warning = models.BooleanField(default = False)

    def __str__(self):
        return self.name


class Show(TimeStampedModel):

    class Meta:
        ordering = ['name']

    name = models.CharField(max_length = 128, unique = True)
    company = models.ForeignKey(Company, on_delete = models.CASCADE, related_name = 'shows')
    image = models.ImageField(upload_to = 'uploads/program/show/', blank = True, default = '')
    description = models.TextField(blank = True, default = '')
    long_description = models.TextField(blank = True, default = '')
    website = models.URLField(max_length = 128, blank = True, default = '')
    facebook = models.CharField(max_length = 64, blank = True, default = '')
    twitter = models.CharField(max_length = 64, blank = True, default = '')
    instagram = models.CharField(max_length = 64, blank = True, default = '')
    genres = models.ManyToManyField(Genre, related_name = 'shows', blank = True)
    age_range = models.CharField(max_length = 16, blank = True, default = '')
    duration = models.PositiveIntegerField(null = True, blank = True)
    venue = models.ForeignKey(Venue, on_delete = models.PROTECT, related_name = 'shows')
    ticketed = models.BooleanField(default = False)
    
    def __str__(self):
        return self.name

    def list_short_description(self):
        return self.description

    def list_long_description(self):
        return self.long_description or self.description

    def display_days(self):
        return ", ".join([performance.date.strftime("%a") for performance in self.performances.all()])

    def display_genres(self):
        return ", ".join([genre.name for genre in self.genres.filter(warning = False)])

    def display_genre_warnings(self):
        return ", ".join([genre.name for genre in self.genres.filter(warning = True)])


class Performance(TimeStampedModel):

    class Meta:
        ordering = ['show', 'date', 'time']
        unique_together = ('show', 'date', 'time')

    show = models.ForeignKey(Show, on_delete = models.CASCADE, related_name = 'performances')
    date = models.DateField(null = True)
    time = models.TimeField(null = True)

    def ticketed(self):
        return self.show.ticketed

    def tickets_sold(self):
        return self.tickets.all().count()

    def tickets_available(self):
        available = self.show.venue.capacity - self.tickets_sold() if self.show.venue.capacity else 0
        return available if available > 0 else 0

    def __str__(self):
        return self.show.name + ' (' + self.date.strftime('%a, %d %b') + ' at ' + self.time.strftime('%H:%M') + ')'


class Review(TimeStampedModel):

    class Meta:
        ordering = ['show', 'source']

    RATING_1STAR = 1
    RATING_2STAR = 2
    RATING_3STAR = 3
    RATING_4STAR = 4
    RATING_5STAR = 5
    RATING_CHOICES = (
        (RATING_1STAR, '*'),
        (RATING_2STAR, '**'),
        (RATING_3STAR, '***'),
        (RATING_4STAR, '****'),
        (RATING_5STAR, '*****'),
    )

    show = models.ForeignKey(Show, on_delete = models.CASCADE, related_name = 'reviews')
    source = models.CharField(max_length = 128)
    rating = models.PositiveIntegerField(null = True, blank = True, choices = RATING_CHOICES)
    body = models.TextField(blank = True, default = '')
    url = models.URLField(max_length = 128, blank = True, default = '')

    def __str__(self):
        return self.show.name + ' (' + str(self.source) + ')'
