import logging
from datetime import datetime, timedelta

import msal
from django.conf import settings
from django.core import signing
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from google_auth_oauthlib.flow import Flow

from profiles.models import Profile

GMAIL_SCOPES = ["https://mail.google.com/"]
OUTLOOK_SCOPES = ["https://outlook.office.com/SMTP.Send", "offline_access"]
logger = logging.getLogger(__name__)


def gmail_connect(request: HttpRequest) -> HttpResponse:
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
    )
    # builds a signed state token containing the user's ID (so you can recover who they are after the redirect)
    state = signing.dumps({"uid": request.user.pk})
    auth_url, _ = flow.authorization_url(state=state, access_type="offline", prompt="consent")
    return redirect(auth_url)


def gmail_callback(request: HttpRequest) -> HttpResponse:
    """Exchange authorization code for tokens and store on user."""
    try:
        data = signing.loads(request.GET["state"], max_age=3600)
        user = Profile.objects.get(pk=data["uid"])
    except (signing.BadSignature, Profile.DoesNotExist):
        return redirect(f"{settings.APP_URL}/settings?oauth=gmail&status=error")

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
        user.email_host = "GMAIL"
        user.email_host_user = user.email
        user.save()
        return redirect(f"{settings.APP_URL}/settings?oauth=gmail&status=success")
    except Exception:
        return redirect(f"{settings.APP_URL}/settings?oauth=gmail&status=error")


def outlook_connect(request: HttpRequest) -> HttpResponse:
    """Redirect user to Microsoft's OAuth consent screen."""

    app = msal.ConfidentialClientApplication(
        settings.MICROSOFT_OAUTH_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{settings.MICROSOFT_OAUTH_TENANT_ID}",
        client_credential=settings.MICROSOFT_OAUTH_CLIENT_SECRET,
    )
    state = signing.dumps({"uid": request.user.pk})
    auth_url = app.get_authorization_request_url(
        scopes=OUTLOOK_SCOPES,
        state=state,
        redirect_uri=settings.MICROSOFT_OAUTH_REDIRECT_URI,
    )
    return redirect(auth_url)


def outlook_callback(request: HttpRequest) -> HttpResponse:
    """Exchange authorization code for tokens and store on user."""
    try:
        data = signing.loads(request.GET["state"], max_age=3600)
        user = Profile.objects.get(pk=data["uid"])
    except (signing.BadSignature, Profile.DoesNotExist):
        return redirect(f"{settings.APP_URL}/settings?oauth=outlook&status=error")

    app = msal.ConfidentialClientApplication(
        settings.MICROSOFT_OAUTH_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{settings.MICROSOFT_OAUTH_TENANT_ID}",
        client_credential=settings.MICROSOFT_OAUTH_CLIENT_SECRET,
    )
    try:
        result = app.acquire_token_by_authorization_code(
            code=request.GET["code"],
            scopes=OUTLOOK_SCOPES,
            redirect_uri=settings.MICROSOFT_OAUTH_REDIRECT_URI,
        )
        if "error" in result:
            return redirect(f"{settings.APP_URL}/settings?oauth=outlook&status=error")

        user.outlook_oauth_refresh_token = result.get("refresh_token", "")
        user.outlook_oauth_access_token = result["access_token"]
        user.outlook_oauth_token_expiry = datetime.now() + timedelta(
            seconds=result.get("expires_in", 3600)
        )
        user.email_host = "OUTLOOK"
        user.email_host_user = user.email
        user.save()
        return redirect(f"{settings.APP_URL}/settings?oauth=outlook&status=success")
    except Exception:
        return redirect(f"{settings.APP_URL}/settings?oauth=outlook&status=error")
