from django.contrib import admin

from .models import Venue, Company, Genre, Show, ShowImage, Performance, Review

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    
    model = Venue
    fieldsets = [
        (None, {
            'fields': ('map_index', 'name', 'image', 'url', 'description', 'color', 'is_ticketed', 'is_searchable', 'is_scheduled', 'capacity', 'box_office', 'email', 'telno'),
        }),
        ('Sponsor', {
            'classes': ('collapse',),
            'fields': ('sponsor_name', 'sponsor_image', 'sponsor_message', 'sponsor_color', 'sponsor_background', 'sponsor_url'),
        }),
        ('Address', {
            'classes': ('collapse',),
            'fields': ('address1', 'address2', 'city', 'post_code'),
        }),
        ('Primary contact', {
            'classes': ('collapse',),
            'fields': ('primary_contact', 'primary_telno', 'primary_mobile', 'primary_email'),
        }),
        ('Secondary contact', {
            'classes': ('collapse',),
            'fields': ('secondary_contact', 'secondary_telno', 'secondary_mobile', 'secondary_email'),
        }),
        ('Social media', {
            'classes': ('collapse',),
            'fields': ('website', 'facebook', 'twitter', 'instagram'),
        }),
    ]

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    
    model = Company
    fieldsets = [
        (None, {
            'fields': ('name', 'image', 'description', 'email', 'telno'),
        }),
        ('Address', {
            'classes': ('collapse',),
            'fields': ('address1', 'address2', 'city', 'post_code'),
        }),
        ('Primary contact', {
            'classes': ('collapse',),
            'fields': ('primary_contact', 'primary_telno', 'primary_mobile', 'primary_email'),
        }),
        ('Secondary contact', {
            'classes': ('collapse',),
            'fields': ('secondary_contact', 'secondary_telno', 'secondary_mobile', 'secondary_email'),
        }),
        ('Social media', {
            'classes': ('collapse',),
            'fields': ('website', 'facebook', 'twitter', 'instagram'),
        }),
    ]
    
    
class ShowImageInline(admin.TabularInline):
    
    model = ShowImage
    extra = 0
    classes = ['collapse']
    
    
class PerformanceInline(admin.TabularInline):
    
    model = Performance
    extra = 0
    classes = ['collapse']


class ReviewInline(admin.StackedInline):
    
    model = Review
    extra = 0
    classes = ['collapse']


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):

    model = Show
    fieldsets = [
        (None, {
            'fields': ('name', 'image', 'company', 'venue', 'description', 'long_description', 'age_range', 'duration', 'is_cancelled', 'replaced_by', 'theatrefest_ID'),
        }),
        ('HTML Description', {
            'classes': ('collapse',),
            'fields': ('html_description',),
        }),
        ('Genres', {
            'classes': ('collapse',),
            'fields': ('genres', 'genre_display', 'has_warnings',),
        }),
        ('Social media', {
            'classes': ('collapse',),
            'fields': ('website', 'facebook', 'twitter', 'instagram'),
        }),
    ]
    filter_horizontal = ['genres']
    inlines = [
        ShowImageInline,
        PerformanceInline,
        ReviewInline,
    ]

    def get_form(self, request, obj = None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['description'].widget.attrs['rows'] = 2
        form.base_fields['long_description'].widget.attrs['rows'] = 4
        form.base_fields['html_description'].widget.attrs['rows'] = 25
        return form


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):

    model = Genre
    fields = ('name',)
