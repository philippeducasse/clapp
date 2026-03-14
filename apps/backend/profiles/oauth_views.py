import logging
from datetime import timedelta

from django.utils import timezone

import msal
from django.conf import settings
from django.core import signing
from rest_framework.request import Request
from rest_framework.response import Response
from django.shortcuts import redirect
from google_auth_oauthlib.flow import Flow
from rest_framework import status
from rest_framework.decorators import api_view

from profiles.models import Profile

GMAIL_SCOPES = ["https://mail.google.com/"]
OUTLOOK_SCOPES = ["https://outlook.office.com/SMTP.Send"]
logger = logging.getLogger(__name__)


@api_view(["GET"])
def gmail_connect(request: Request) -> Response:
    logger.info(f"Attempting to connect user {request.user.email} to Gmail")
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=GMAIL_SCOPES,
        redirect_uri=settings.GOOGLE_OAUTH_REDIRECT_URI,
        autogenerate_code_verifier=False,
    )
    state = signing.dumps({"uid": request.user.pk})
    auth_url, _ = flow.authorization_url(state=state, access_type="offline", prompt="consent")
    return Response({"auth_url": auth_url}, status=status.HTTP_200_OK)


def gmail_callback(request: Request) -> Response:
    logger.info(f"Returning from Google OATH for user {request.GET['state']} ")
    """Exchange authorization code for tokens and store on user."""
    try:
        data = signing.loads(request.GET["state"], max_age=3600)
        user = Profile.objects.get(pk=data["uid"])
    except (signing.BadSignature, Profile.DoesNotExist):
        return redirect(f"{settings.APP_URL}/profile#email-settings?oauth=gmail&status=error")

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=GMAIL_SCOPES,
        redirect_uri=settings.GOOGLE_OAUTH_REDIRECT_URI,
    )
    try:
        flow.fetch_token(code=request.GET["code"])
        creds = flow.credentials
        user.google_oauth_refresh_token = creds.refresh_token or ""
        user.google_oauth_access_token = creds.token
        user.google_oauth_token_expiry = creds.expiry
        # Clear any existing Outlook tokens to avoid conflicts
        user.outlook_oauth_refresh_token = ""
        user.outlook_oauth_access_token = ""
        user.outlook_oauth_token_expiry = None
        user.email_host = "GMAIL"
        user.email_host_user = user.email
        user.save()
        return redirect(f"{settings.APP_URL}/profile#email-settings?oauth=gmail&status=success")
    except Exception as e:
        logger.exception(f"Gmail token exchange failed: {e}")
        return redirect(f"{settings.APP_URL}/profile#email-settings?oauth=gmail&status=error")


@api_view(["GET"])
def outlook_connect(request: Request) -> Response:
    logger.info(f"Attempting to connect user {request.user.email} to Gmail")
    """Redirect user to Microsoft's OAuth consent screen."""

    app = msal.ConfidentialClientApplication(
        settings.MICROSOFT_OAUTH_CLIENT_ID,
        authority="https://login.microsoftonline.com/common",
        client_credential=settings.MICROSOFT_OAUTH_CLIENT_SECRET,
    )
    state = signing.dumps({"uid": request.user.pk})
    auth_url = app.get_authorization_request_url(
        scopes=OUTLOOK_SCOPES,
        state=state,
        redirect_uri=settings.MICROSOFT_OAUTH_REDIRECT_URI,
    )
    print("AUTH:URL:", auth_url)
    return Response({"auth_url": auth_url}, status=status.HTTP_200_OK)


def outlook_callback(request: Request) -> Response:
    logger.info(f"Returning from Outlook OATH for user {request.GET['state']} ")
    """Exchange authorization code for tokens and store on user."""
    try:
        data = signing.loads(request.GET["state"], max_age=3600)
        user = Profile.objects.get(pk=data["uid"])
    except (signing.BadSignature, Profile.DoesNotExist):
        return redirect(f"{settings.APP_URL}/profile#email-settings?oauth=outlook&status=error")

    app = msal.ConfidentialClientApplication(
        settings.MICROSOFT_OAUTH_CLIENT_ID,
        authority="https://login.microsoftonline.com/common",
        client_credential=settings.MICROSOFT_OAUTH_CLIENT_SECRET,
    )
    try:
        result = app.acquire_token_by_authorization_code(
            code=request.GET["code"],
            scopes=OUTLOOK_SCOPES,
            redirect_uri=settings.MICROSOFT_OAUTH_REDIRECT_URI,
        )
        if "error" in result:
            return redirect(f"{settings.APP_URL}/profile#email-settings?oauth=outlook&status=error")

        user.outlook_oauth_refresh_token = result.get("refresh_token", "")
        user.outlook_oauth_access_token = result["access_token"]
        user.outlook_oauth_token_expiry = timezone.now() + timedelta(
            seconds=result.get("expires_in", 3600)
        )
        # Clear any existing Gmail tokens to avoid conflicts
        user.google_oauth_refresh_token = ""
        user.google_oauth_access_token = ""
        user.google_oauth_token_expiry = None
        user.email_host = "OUTLOOK"
        user.email_host_user = user.email
        user.save()
        return redirect(f"{settings.APP_URL}/profile#email-settings?oauth=outlook&status=success")
    except Exception:
        return redirect(f"{settings.APP_URL}/profile#email-settings?oauth=outlook&status=error")


@api_view(["POST"])
def oauth_disconnect(request: Request) -> Response:
    """Remove OAuth connection and clear all stored tokens."""
    user = request.user
    user.google_oauth_refresh_token = ""
    user.google_oauth_access_token = ""
    user.google_oauth_token_expiry = None
    user.outlook_oauth_refresh_token = ""
    user.outlook_oauth_access_token = ""
    user.outlook_oauth_token_expiry = None
    user.email_host = ""
    user.email_host_user = ""
    user.save()
    logger.info(f"User {user.email} disconnected OAuth")
    return Response({"message": "OAuth connection removed"}, status=status.HTTP_200_OK)
