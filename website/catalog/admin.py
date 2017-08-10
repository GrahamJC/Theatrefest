from django.contrib import admin

from .models import Venue, Company, Genre, PaymentType, Show, Performance, Review

admin.site.register(Venue)
admin.site.register(Genre)
admin.site.register(PaymentType)
admin.site.register(Performance)
admin.site.register(Review)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    
    model = Company
    fieldsets = [
        (None, {
            'fields': ('name', 'image', 'description', 'email', 'telno'),
        }),
        ('Social media', {
            'classes': ('collapse',),
            'fields': ('website', 'facebook', 'twitter', 'instagram'),
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
            'fields': ('name', 'company', 'venue', 'description', 'payment_type', 'age_range', 'duration'),
        }),
        ('Social media', {
            'classes': ('collapse',),
            'fields': ('website', 'facebook', 'twitter', 'instagram'),
        }),
        ('Genres', {
            'classes': ('collapse',),
            'fields': ('genres',),
        }),
    ]
    filter_horizontal = ['genres']
    inlines = [
        PerformanceInline,
        ReviewInline,
    ]
