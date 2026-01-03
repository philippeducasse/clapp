from django.contrib import admin
from django.utils.html import format_html

from organisations.venues.models import Venue, VenueContact


class SoftDeleteFilter(admin.SimpleListFilter):
    title = "Deletion Status"
    parameter_name = "deleted"

    def lookups(self, request, model_admin):
        return (
            ("active", "Active only"),
            ("deleted", "Deleted only"),
        )

    def queryset(self, request, queryset):
        if self.value() == "active":
            return queryset.filter(deleted_at__isnull=True)
        elif self.value() == "deleted":
            return queryset.filter(deleted_at__isnull=False)
        # Default: show all
        return queryset


class VenueContactInline(admin.TabularInline):
    model = VenueContact
    extra = 1

    def get_queryset(self, request):
        """Include soft-deleted contacts in admin"""
        qs = super().get_queryset(request)
        return qs.model.objects.with_deleted().filter(venue=self.parent_instance)


class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "venue_type", "country", "deleted_status")
    list_filter = (SoftDeleteFilter, "venue_type", "country")
    search_fields = ("name", "venue_type", "country")
    inlines = [VenueContactInline]
    readonly_fields = ("deleted_at",)

    def get_queryset(self, request):
        """Show all venues (active + deleted) by default"""
        return self.model.objects.with_deleted()

    def deleted_status(self, obj):
        """Display deletion status with visual indicator"""
        if obj.deleted_at:
            return format_html('<span style="color: red; font-weight: bold;">🗑️ Deleted</span>')
        return format_html('<span style="color: green;">✓ Active</span>')

    deleted_status.short_description = "Status"

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions["restore_venues"] = (
            self.restore_venues,
            "restore_venues",
            "Restore selected venues",
        )
        return actions

    def restore_venues(self, request, queryset):
        """Admin action to restore soft-deleted venues"""
        restored_count = 0
        for venue in queryset.filter(deleted_at__isnull=False):
            venue.restore()
            restored_count += 1
        self.message_user(request, f"Successfully restored {restored_count} venue(s).")

    restore_venues.short_description = "Restore selected venues"


admin.site.register(Venue, VenueAdmin)
