"""Read replies to application emails and suggest a new status. Every suggestion needs approval.

Only replies are kept: an email is imported when its In-Reply-To or References header contains
the Message-ID we stored on an Application when sending it (Application.sent_message_id).
"""

import logging
import os
import re
from datetime import date, timedelta
from typing import Literal, Optional

from imap_tools import AND, MailBox, MailMessage
from pydantic import BaseModel

from applications.models import APPLICATION_STATUS, Application, InboundEmail
from services.mistral_service import MistralClient

logger = logging.getLogger(__name__)

DAYS_TO_CHECK = 3

StatusLiteral = Literal[tuple(value for value, _ in APPLICATION_STATUS)]  # type: ignore[valid-type]


class EmailClassification(BaseModel):
    suggested_status: Optional[StatusLiteral]  # type: ignore[valid-type]
    summary: str


def fetch_recent_emails() -> list[MailMessage]:
    """Fetch the last few days of mail. Already imported emails are skipped later."""
    with MailBox(os.getenv("IMAP_HOST", "ssl0.ovh.net")).login(
        os.environ["IMAP_USERNAME"], os.environ["IMAP_PASSWORD"]
    ) as mailbox:
        since = date.today() - timedelta(days=DAYS_TO_CHECK)
        return list(mailbox.fetch(AND(date_gte=since), mark_seen=False))


BULK_HEADERS = ("list-id", "list-unsubscribe")
BULK_PRECEDENCE = ("bulk", "list", "junk")
BOUNCE_SENDERS = ("mailer-daemon@", "postmaster@")


def is_skipped(message: MailMessage) -> bool:
    """Mailing lists, newsletters, bounces and our own messages. Auto-replies are kept."""
    headers = message.headers
    if any(name in headers for name in BULK_HEADERS):
        return True
    precedence = " ".join(headers.get("precedence", ())).strip().lower()
    if precedence in BULK_PRECEDENCE:
        return True
    sender = message.from_.lower()
    if sender.startswith(BOUNCE_SENDERS):
        return True
    return sender == os.getenv("IMAP_USERNAME", "").lower()


def is_auto_reply(message: MailMessage) -> bool:
    headers = message.headers
    auto_submitted = " ".join(headers.get("auto-submitted", ())).strip().lower()
    return (
        (auto_submitted not in ("", "no")) or "x-autoreply" in headers or "x-autorespond" in headers
    )


def find_application(message: MailMessage) -> Optional[Application]:
    """Find the application this email replies to, using the reply headers."""
    headers = " ".join(
        message.headers.get("in-reply-to", ()) + message.headers.get("references", ())
    )
    message_ids = re.findall(r"<[^<>\s]+>", headers)
    if not message_ids:
        return None
    return Application.objects.filter(sent_message_id__in=message_ids).first()


def classify(application: Application, body: str) -> EmailClassification:
    statuses = ", ".join(value for value, _ in APPLICATION_STATUS)
    prompt = f"""A performing artist applied to "{application.organisation}" and received this reply.
Suggest the new status of the application, one of: {statuses}.
Use null if the email is an automatic reply or does not change anything.
Write a one-sentence summary of the reply in English.

Application email:
{application.message[:3000]}

Reply:
{body[:5000]}"""
    return MistralClient().parse(prompt, EmailClassification)


def import_email(message: MailMessage) -> Optional[InboundEmail]:
    """Save a reply with a suggested status. Returns None if it is not a new reply."""
    message_id = " ".join(message.headers.get("message-id", ())).strip()
    if not message_id or InboundEmail.objects.filter(message_id=message_id).exists():
        return None
    if is_skipped(message):
        return None

    application = find_application(message)
    if application is None:
        return None

    body = message.text or message.html
    result = classify(application, body)
    return InboundEmail.objects.create(
        application=application,
        message_id=message_id,
        from_address=message.from_,
        subject=message.subject,
        body=body,
        received_at=message.date,
        suggested_status=result.suggested_status or "",
        summary=result.summary,
    )


def check_inbox() -> int:
    """Import new replies. Returns how many were imported."""
    imported = [import_email(message) for message in fetch_recent_emails()]
    count = len([email for email in imported if email])
    logger.info("Imported %d application replies", count)
    return count
