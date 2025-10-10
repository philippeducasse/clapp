from django.contrib import admin
from organisations.venues.models import Venue


class VenueAdmin(admin.ModelAdmin):
    pass


admin.site.register(Venue, VenueAdmin)
