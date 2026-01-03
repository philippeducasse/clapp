from django.contrib import admin
from django.utils.html import format_html

from organisations.festivals.models import Festival, FestivalContact


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


class FestivalContactInline(admin.TabularInline):
    model = FestivalContact
    extra = 1

    def get_queryset(self, request):
        """Include soft-deleted contacts in admin"""
        qs = super().get_queryset(request)
        return qs.model.objects.with_deleted().filter(festival=self.parent_instance)


class FestivalAdmin(admin.ModelAdmin):
    list_display = ("name", "festival_type", "country", "deleted_status")
    list_filter = (SoftDeleteFilter, "festival_type", "country")
    search_fields = ("name", "festival_type", "country")
    inlines = [FestivalContactInline]
    readonly_fields = ("deleted_at",)

    def get_queryset(self, request):
        """Show all festivals (active + deleted) by default"""
        return self.model.objects.with_deleted()

    def deleted_status(self, obj):
        """Display deletion status with visual indicator"""
        if obj.deleted_at:
            return format_html('<span style="color: red; font-weight: bold;">🗑️ Deleted</span>')
        return format_html('<span style="color: green;">✓ Active</span>')

    deleted_status.short_description = "Status"

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions["restore_festivals"] = (
            self.restore_festivals,
            "restore_festivals",
            "Restore selected festivals",
        )
        actions["hard_delete_festivals"] = (
            self.hard_delete_festivals,
            "hard_delete_festivals",
            "Permanently delete selected festivals",
        )
        return actions

    def restore_festivals(self, request, queryset):
        """Admin action to restore soft-deleted festivals"""
        restored_count = 0
        for festival in queryset.filter(deleted_at__isnull=False):
            festival.restore()
            restored_count += 1
        self.message_user(request, f"Successfully restored {restored_count} festival(s).")

    restore_festivals.short_description = "Restore selected festivals"

    def hard_delete_festivals(self, request, queryset):
        """Admin action to hard_delete soft-deleted festivals"""
        hard_deleted_count = 0
        for festival in queryset:
            festival.hard_delete()
            hard_deleted_count += 1
        self.message_user(request, f"Successfully hard_deleted {hard_deleted_count} festival(s).")

    hard_delete_festivals.short_description = "hard_delete selected festivals"


admin.site.register(Festival, FestivalAdmin)
