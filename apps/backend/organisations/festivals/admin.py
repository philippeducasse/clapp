from django.contrib import admin
from organisations.festivals.models import Festival, FestivalContact


class FestivalContactInline(admin.TabularInline):
    model = FestivalContact
    extra = 1


class FestivalAdmin(admin.ModelAdmin):
    list_display = ("name", "festival_type")
    list_filters = ("festival_type",)
    search_fields = ("name", "festival_type")
    inlines = [FestivalContactInline]


admin.site.register(Festival, FestivalAdmin)
