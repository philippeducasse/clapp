from django.db import models

from profiles.models import Profile


class BugReport(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("investigating", "Investigating"),
        ("fixed", "Fixed"),
        ("wontfix", "Won't Fix"),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    message = models.TextField(max_length=15000)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bug Report from {self.profile} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ["-created_at"]


class BugReportAttachment(models.Model):
    bug_report = models.ForeignKey(BugReport, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="bug_reports/")
    created_at = models.DateTimeField(auto_now_add=True)
