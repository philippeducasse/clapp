from datetime import datetime, timedelta

import msal
from django.conf import settings
from django.core.mail import get_connection
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from profiles.models import EMAIL_HOST_MAPPING, Profile
from profiles.oauth_smtp_backend import XOAuth2EmailBackend


def get_user_email_connection(user: Profile):
    """Get SMTP connection for user, handling OAuth or manual SMTP."""
    # Try OAuth if tokens exist
    if user.email_host == "GMAIL" and user.google_oauth_refresh_token:
        return _gmail_oauth_connection(user)
    if user.email_host == "OUTLOOK" and user.outlook_oauth_refresh_token:
        return _outlook_oauth_connection(user)

    # Fall back to manual SMTP (app passwords)
    if user.email_host == "OTHER":
        smtp_host = user.other_email_host
    else:
        smtp_host = EMAIL_HOST_MAPPING.get(user.email_host, user.email_host)

    if not smtp_host:
        raise Exception("No smtp host found!")

    if not user.email_host_user:
        raise Exception("No email host user found!")

    return get_connection(
        backend="django.core.mail.backends.smtp.EmailBackend",
        host=smtp_host,
        port=user.email_port,
        username=user.email_host_user,
        password=user.email_host_password,
        use_tls=user.email_use_tls,
    )


def _gmail_oauth_connection(user: Profile):
    """Create SMTP connection using Gmail OAuth tokens, refreshing if needed."""
    creds = Credentials(
        token=user.google_oauth_access_token,
        refresh_token=user.google_oauth_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
    )

    # Refresh if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        user.google_oauth_access_token = creds.token
        user.google_oauth_token_expiry = creds.expiry
        user.save(update_fields=["google_oauth_access_token", "google_oauth_token_expiry"])

    return XOAuth2EmailBackend(
        host="smtp.gmail.com",
        port=587,
        username=user.email_host_user,
        use_tls=True,
        access_token=creds.token,
    )


def _outlook_oauth_connection(user: Profile):
    """Create SMTP connection using Outlook OAuth tokens, refreshing if needed."""
    app = msal.ConfidentialClientApplication(
        settings.MICROSOFT_OAUTH_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{settings.MICROSOFT_OAUTH_TENANT_ID}",
        client_credential=settings.MICROSOFT_OAUTH_CLIENT_SECRET,
    )

    # Refresh if expired
    if (
        user.outlook_oauth_token_expiry
        and user.outlook_oauth_token_expiry <= datetime.now()
        and user.outlook_oauth_refresh_token
    ):
        result = app.acquire_token_by_refresh_token(
            user.outlook_oauth_refresh_token, scopes=["https://outlook.office.com/SMTP.Send"]
        )
        if "access_token" in result:
            user.outlook_oauth_access_token = result["access_token"]
            user.outlook_oauth_token_expiry = datetime.now() + timedelta(
                seconds=result.get("expires_in", 3600)
            )
            user.save(update_fields=["outlook_oauth_access_token", "outlook_oauth_token_expiry"])

    return XOAuth2EmailBackend(
        host="smtp.office365.com",
        port=587,
        username=user.email_host_user,
        use_tls=True,
        access_token=user.outlook_oauth_access_token,
    )
