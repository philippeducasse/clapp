from django.contrib import admin
from performances.models import Performance, Dossier


class DossierInline(admin.TabularInline):
    model = Dossier
    extra = 1  # Number of empty forms to display
    fields = ["file", "uploaded_at"]
    readonly_fields = ["uploaded_at"]


class PerformanceAdmin(admin.ModelAdmin):
    inlines = [DossierInline]


admin.site.register(Performance, PerformanceAdmin)
