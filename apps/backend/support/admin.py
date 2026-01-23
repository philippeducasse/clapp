from django.contrib import admin

from .models import BugReport, BugReportAttachment


class BugReportAttachmentInline(admin.TabularInline):
    model = BugReportAttachment
    extra = 0
    fields = ("file", "created_at")
    readonly_fields = ("created_at",)


@admin.register(BugReport)
class BugReportAdmin(admin.ModelAdmin):
    list_display = ("profile", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("message", "profile__user__username")
    readonly_fields = ("created_at",)
    inlines = [BugReportAttachmentInline]
