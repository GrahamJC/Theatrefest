from django.contrib import admin

from .models import Venue, Company, Genre, Show, Performance, Review

admin.site.register(Genre)
admin.site.register(Performance)
admin.site.register(Review)

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    
    model = Venue
    fieldsets = [
        (None, {
            'fields': ('name', 'image', 'description', 'capacity', 'email', 'telno', 'color'),
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
            'fields': ('name', 'image', 'company', 'venue', 'description', 'age_range', 'duration', 'ticketed'),
        }),
        ('Genres', {
            'classes': ('collapse',),
            'fields': ('genres',),
        }),
        ('Social media', {
            'classes': ('collapse',),
            'fields': ('website', 'facebook', 'twitter', 'instagram'),
        }),
    ]
    filter_horizontal = ['genres']
    inlines = [
        PerformanceInline,
        ReviewInline,
    ]
