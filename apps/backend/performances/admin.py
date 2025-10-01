from django.contrib import admin
from .models import Performance, Dossier


class DossierInline(admin.TabularInline):
    model = Dossier
    extra = 1  # Number of empty forms to display
    fields = ("file", "uploaded_at")
    readonly_fields = ("uploaded_at",)


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = (
        "performance_title",
        "profile",
        "performance_type",
        "creation_date",
        "dossier_count",
    )
    list_filter = ("performance_type", "genres", "creation_date")
    search_fields = ("performance_title", "short_description")

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("profile", "performance_title", "short_description")},
        ),
        (
            "Details",
            {
                "fields": (
                    "performance_type",
                    "genres",
                    "length",
                    "creation_date",
                    "trailer",
                )
            },
        ),
        (
            "Description",
            {
                "fields": ("long_description",),
                "classes": ("collapse",),  # Makes this section collapsible
            },
        ),
        (
            "Legacy Dossier",
            {
                "fields": ("dossier",),
                "description": "Old single dossier field (deprecated - use Dossiers section below)",
            },
        ),
    )

    inlines = [DossierInline]

    def dossier_count(self, obj):
        return obj.dossiers.count()

    dossier_count.short_description = "Number of Dossiers"


@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = ("performance", "file", "uploaded_at")
    list_filter = ("uploaded_at",)
    search_fields = ("performance__performance_title",)
    readonly_fields = ("uploaded_at",)
