from django.contrib import admin

from discovery.models import DiscoveryCandidate, DiscoveryRun, DiscoverySource


@admin.register(DiscoveryRun)
class DiscoveryRunAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "starting_point", "created_by", "created_at", "finished_at")
    list_filter = ("status",)
    search_fields = ("starting_point",)
    readonly_fields = ("created_at", "started_at", "finished_at", "last_heartbeat_at")


@admin.register(DiscoveryCandidate)
class DiscoveryCandidateAdmin(admin.ModelAdmin):
    list_display = ("name", "org_type", "country", "domain", "state", "run", "created_at")
    list_filter = ("state", "org_type")
    search_fields = ("name", "domain", "country", "town")
    readonly_fields = ("created_at", "reviewed_at", "seed_content_type", "seed_object_id")


@admin.register(DiscoverySource)
class DiscoverySourceAdmin(admin.ModelAdmin):
    list_display = ("domain", "kind", "leads_found", "candidates_accepted", "last_visited_at")
    list_filter = ("kind",)
    search_fields = ("url", "domain", "title")
