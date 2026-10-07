"""Read emails about applications and suggest a new status. Every suggestion needs approval.

1. Skip mailing lists, bounces and our own messages (auto-replies are kept).
2. Find candidate applications (applications/matching.py): reply headers, sender, domain, name.
3. Emails without candidates only go to Mistral if they contain a keyword.
4. Mistral picks the application among the candidates and suggests a status.
"""

import logging
import os
import re
import unicodedata
from datetime import date, timedelta
from typing import Literal, Optional

from imap_tools import AND, MailBox, MailMessage
from pydantic import BaseModel

from applications.matching import Candidates, find_candidates
from applications.models import APPLICATION_STATUS, Application, InboundEmail
from profiles.models import Profile
from services.mistral_service import MistralClient

logger = logging.getLogger(__name__)

DAYS_TO_CHECK = 3

StatusLiteral = Literal[tuple(value for value, _ in APPLICATION_STATUS)]  # type: ignore[valid-type]


class EmailClassification(BaseModel):
    is_application_related: bool
    application_id: Optional[int]
    suggested_status: Optional[StatusLiteral]  # type: ignore[valid-type]
    is_auto_reply: bool
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

# Words (accents removed) that suggest an email is about booking or applying.
# Stems match the start of a word: "festival" also matches "festivals", "program" matches
# "programme", "programmation", "programmazione"...
KEYWORD_STEMS = (
    # en
    "festival", "booking", "program", "lineup", "line-up", "perform", "residenc",
    "application", "invitation", "invite", "audition",
    # de
    "auftritt", "auftreten", "vorstellung", "auffuhrung", "gastspiel", "bewerbung",
    "beworben", "anfrage", "einladung", "honorar", "veranstalt", "spielplan",
    # fr
    "spectacle", "representation", "candidature", "postul", "tournee",
    # es / it
    "espectaculo", "actuacion", "candidatura", "solicitud", "spettacolo", "esibizione",
    "residenza",
    # nl
    "voorstelling", "optreden", "aanvraag", "sollicitatie",
)  # fmt: skip
# Short words match whole words only (plural "s" allowed): "show" must not match "shower".
KEYWORD_WORDS = (
    "show", "apply", "applied", "tour", "venue", "stage", "buhne", "gage", "cachet",
    "scene", "gira",
)  # fmt: skip
KEYWORD_PATTERN = re.compile(
    r"\b(?:"
    + "|".join(map(re.escape, KEYWORD_STEMS))
    + r")|\b(?:"
    + "|".join(map(re.escape, KEYWORD_WORDS))
    + r")s?\b"
)
KEYWORD_SEARCH_CHARS = 5000


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


def mentions_keyword(message: MailMessage) -> bool:
    """Cheap check before sending an unmatched email to Mistral."""
    body = message.text or message.html or ""
    # Make body more search friendly by normalising text
    text = unicodedata.normalize("NFKD", f"{message.subject}\n{body[:KEYWORD_SEARCH_CHARS]}")
    text = "".join(c for c in text if not unicodedata.combining(c)).lower()
    return KEYWORD_PATTERN.search(text) is not None


def is_auto_reply(message: MailMessage) -> bool:
    headers = message.headers
    auto_submitted = " ".join(headers.get("auto-submitted", ())).strip().lower()
    return (
        (auto_submitted not in ("", "no")) or "x-autoreply" in headers or "x-autorespond" in headers
    )


def inbox_profile() -> Optional[Profile]:
    """The profile that owns the inbox. Without it, only replies (HEADER) can be matched."""
    return Profile.objects.filter(email__iexact=os.getenv("IMAP_USERNAME", "")).first()


def describe(application: Application, message_chars: int) -> str:
    organisation = application.organisation
    return f"""- id: {application.id}
  organisation: {organisation.name if organisation else "unknown"}
  season: {application.season.name if application.season else "none"}
  status: {application.status}
  applied on: {application.application_date or "not sent"}
  application email: {application.message[:message_chars] or "none (applied outside the app)"}"""


def classify(message: MailMessage, candidates: Candidates) -> EmailClassification:
    statuses = ", ".join(value for value, _ in APPLICATION_STATUS)
    message_chars = 3000 if len(candidates.applications) == 1 else 500
    applications = "\n".join(describe(a, message_chars) for a in candidates.applications)
    organisations = ", ".join(o.name for o in candidates.organisations)
    body = message.text or message.html or ""
    prompt = f"""A performing artist (circus, street theatre) applies to festivals, venues and residencies.
Read the email below that the artist received.

1. is_application_related: is it about one of the artist's applications, or about booking,
   inviting or programming the artist? Newsletters, invoices and personal mail are not.
2. application_id: the id of the application it is about, chosen from the candidates below.
   Use null if none of them fits.
3. suggested_status: the new status of that application, one of: {statuses}.
   - A confirmation that an application was received, for a DRAFT application: APPLIED.
   - Never move an application backwards (e.g. from IN_DISCUSSION or ACCEPTED to APPLIED).
   - Use null if the email does not change anything.
4. is_auto_reply: is it an automatic reply (out of office, automatic confirmation)?
5. summary: one sentence in English. For an out-of-office reply, include the return date.

Candidate applications:
{applications or "none"}

Organisations the sender may belong to: {organisations or "unknown"}

Email:
From: {message.from_values.full if message.from_values else message.from_}
Subject: {message.subject}

{body[:5000]}"""
    return MistralClient().parse(prompt, EmailClassification)


def choose_application(
    candidates: Candidates, result: EmailClassification
) -> Optional[Application]:
    if candidates.method == "HEADER":
        return candidates.applications[0]
    if not result.is_application_related:
        return None
    return next((a for a in candidates.applications if a.id == result.application_id), None)


def import_email(message: MailMessage) -> Optional[InboundEmail]:
    """Save an email about an application with a suggested status. Returns None if it is
    already imported or not about an application."""
    message_id = " ".join(message.headers.get("message-id", ())).strip()
    if not message_id or InboundEmail.objects.filter(message_id=message_id).exists():
        return None
    if is_skipped(message):
        return None

    candidates = find_candidates(message, inbox_profile())
    if candidates.method == "NONE" and not mentions_keyword(message):
        return None

    result = classify(message, candidates)
    application = choose_application(candidates, result)
    if application is None:
        # Kept as UNMATCHED once InboundEmail.application is nullable (step 5).
        return None

    return InboundEmail.objects.create(
        application=application,
        message_id=message_id,
        from_address=message.from_,
        subject=message.subject,
        body=message.text or message.html,
        received_at=message.date if message.date_str else None,
        suggested_status=result.suggested_status or "",
        summary=result.summary,
    )


def check_inbox() -> int:
    """Import new emails about applications. Returns how many were imported."""
    imported = [import_email(message) for message in fetch_recent_emails()]
    count = len([email for email in imported if email])
    logger.info("Imported %d application emails", count)
    return count
