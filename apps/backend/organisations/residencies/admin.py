from django.contrib import admin
from organisations.residencies.models import Residency


class ResidencyAdmin(admin.ModelAdmin):
    pass


admin.site.register(Residency, ResidencyAdmin)
