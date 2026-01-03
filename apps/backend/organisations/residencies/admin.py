from django.contrib import admin
from django.utils.html import format_html

from organisations.residencies.models import Residency, ResidencyContact


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


class ResidencyContactInline(admin.TabularInline):
    model = ResidencyContact
    extra = 1

    def get_queryset(self, request):
        """Include soft-deleted contacts in admin"""
        qs = super().get_queryset(request)
        return qs.model.objects.with_deleted()


class ResidencyAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "deleted_status")
    list_filter = (SoftDeleteFilter, "country")
    search_fields = ("name", "country")
    inlines = [ResidencyContactInline]
    readonly_fields = ("deleted_at",)
    actions = ["restore_residencies", "hard_delete_residencies"]

    def get_queryset(self, request):
        """Show all residencies (active + deleted) by default"""
        return self.model.objects.with_deleted()

    def deleted_status(self, obj):
        """Display deletion status with visual indicator"""
        if obj.deleted_at:
            return format_html('<span style="color: red; font-weight: bold;">🗑️ Deleted</span>')
        return format_html('<span style="color: green;">✓ Active</span>')

    deleted_status.short_description = "Status"

    def restore_residencies(self, request, queryset):
        """Admin action to restore soft-deleted residencies"""
        restored_count = 0
        for residency in queryset.filter(deleted_at__isnull=False):
            residency.restore()
            restored_count += 1
        self.message_user(request, f"Successfully restored {restored_count} residency/residencies.")

    restore_residencies.short_description = "Restore selected residencies"

    def hard_delete_residencies(self, request, queryset):
        """Admin action to permanently delete residencies"""
        hard_deleted_count = 0
        for residency in queryset:
            residency.hard_delete()
            hard_deleted_count += 1
        self.message_user(
            request, f"Successfully permanently deleted {hard_deleted_count} residency/residencies."
        )

    hard_delete_residencies.short_description = "Permanently delete selected residencies"


admin.site.register(Residency, ResidencyAdmin)
