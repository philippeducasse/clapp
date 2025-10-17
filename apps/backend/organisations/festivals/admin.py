from django.contrib import admin
from organisations.festivals.models import Festival


class FestivalAdmin(admin.ModelAdmin):
    list_display = ("name", "festival_type")
    list_filters = ("festival_type",)
    search_fields = ("name", "festival_type")


admin.site.register(Festival, FestivalAdmin)
