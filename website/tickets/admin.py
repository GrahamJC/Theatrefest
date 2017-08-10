from django.contrib import admin

from .models import BoxOffice, FringerType, Fringer, TicketType, Ticket

admin.site.register(BoxOffice)
admin.site.register(FringerType)
admin.site.register(Fringer)
admin.site.register(TicketType)
admin.site.register(Ticket)

