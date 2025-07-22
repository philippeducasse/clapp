from django.contrib import admin
from festivals.models import Festival


class FestivalAdmin(admin.ModelAdmin):
    pass


admin.site.register(Festival, FestivalAdmin)
