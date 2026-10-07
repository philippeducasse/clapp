from django.contrib import admin

from applications.models import Application, ApplicationSeason, InboundEmail


class ApplicationAdmin(admin.ModelAdmin):
    pass


class ApplicationSeasonAdmin(admin.ModelAdmin):
    pass


admin.site.register(Application, ApplicationAdmin)
admin.site.register(ApplicationSeason, ApplicationSeasonAdmin)


@admin.register(InboundEmail)
class InboundEmailAdmin(admin.ModelAdmin):
    list_display = (
        "received_at",
        "from_address",
        "subject",
        "match_method",
        "suggested_status",
        "state",
    )
    list_filter = ("state", "match_method", "is_auto_reply")
