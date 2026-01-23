from rest_framework import serializers
from .models import BugReport, BugReportAttachment


class BugReportAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BugReportAttachment
        fields = ["file"]


class BugReportSerializer(serializers.ModelSerializer):
    attachments = BugReportAttachmentSerializer(many=True, required=False)

    class Meta:
        model = BugReport
        fields = ["message", "attachments"]

    def create(self, validated_data):
        attachments_data = validated_data.pop("attachments", [])
        bug_report = BugReport.objects.create(**validated_data)

        for attachment_data in attachments_data:
            BugReportAttachment.objects.create(bug_report=bug_report, **attachment_data)

        return bug_report
