from django.contrib import admin

from applications.models import Application, ApplicationSeason


class ApplicationAdmin(admin.ModelAdmin):
    pass


class ApplicationSeasonAdmin(admin.ModelAdmin):
    pass


admin.site.register(Application, ApplicationAdmin)
admin.site.register(ApplicationSeason, ApplicationSeasonAdmin)
