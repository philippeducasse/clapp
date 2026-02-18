from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import BugReportSerializer


class SubmitBugReportView(APIView):
    def post(self, request):
        serializer = BugReportSerializer(data=request.data)
        if serializer.is_valid():
            bug_report = serializer.save(profile=request.user)
            # Send email
            email = EmailMultiAlternatives(
                subject=f"Bug Report from {request.user}",
                body=bug_report.message,
                from_email=settings.APP_EMAIL,
                to=[settings.APP_EMAIL],
            )
            # Attach files
            for attachment in bug_report.attachments.all():
                email.attach_file(attachment.file.path)

            email.send()

            return Response({"status": "Bug report submitted"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
