from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Profile


class CustomUserAdmin(UserAdmin):
    model = Profile
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "company_name",
                    "personal_website",
                    "location",
                    "nationality",
                    "instagram_profile",
                    "facebook_profile",
                    "tiktok_profile",
                    "phone",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Email settings",
            {
                "fields": (
                    "email_host",
                    "email_host_user",
                    "other_email_host",
                    "email_port",
                    "email_host_password",
                    "email_use_tls",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


admin.site.register(Profile, CustomUserAdmin)
