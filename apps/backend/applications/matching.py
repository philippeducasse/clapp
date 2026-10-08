"""Find the applications an inbound email could be about.

Methods are tried in order and the first one that finds something wins:
HEADER (reply headers), SENDER (exact address), DOMAIN (sender domain), NAME (organisation
name in the text, or its distinctive words). Web form confirmations (FORM) look for the
organisation by name instead, as there is usually no application yet. Organisations found
without an application are returned too, so an application can be created from the email.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, Callable, Iterable, Optional

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from imap_tools import MailMessage

from applications.models import Application
from organisations.festivals.models import Festival
from organisations.residencies.models import Residency
from organisations.utils import normalize_domain
from organisations.venues.models import Venue
from profiles.models import Profile

ORGANISATION_MODELS = (Festival, Venue, Residency)

FREE_MAIL_DOMAINS = {
    "gmail.com",
    "googlemail.com",
    "outlook.com",
    "hotmail.com",
    "hotmail.fr",
    "hotmail.de",
    "live.com",
    "live.fr",
    "msn.com",
    "yahoo.com",
    "yahoo.fr",
    "yahoo.de",
    "icloud.com",
    "me.com",
    "aol.com",
    "gmx.de",
    "gmx.net",
    "gmx.at",
    "gmx.ch",
    "web.de",
    "t-online.de",
    "freenet.de",
    "posteo.de",
    "mailbox.org",
    "orange.fr",
    "free.fr",
    "laposte.net",
    "sfr.fr",
    "wanadoo.fr",
    "protonmail.com",
    "proton.me",
}

# Organisation names that are too short or too common to be found in a text reliably.
NAME_MIN_LENGTH = 5
GENERIC_NAMES = {
    "festival",
    "theatre",
    "theater",
    "circus",
    "cirque",
    "zirkus",
    "street",
    "kultur",
    "culture",
    "summer",
    "sommer",
}
NAME_SEARCH_CHARS = 2000
NAME_SEARCH_DAYS = 365

# Words that do not identify an organisation on their own, ignored when matching names by
# tokens: "Ascona Street Festival" is found by "ascona" alone. Written without accents.
GENERIC_WORDS = GENERIC_NAMES | {
    # en
    "festivals", "fest", "international", "artists", "artist", "arts", "theatres", "theaters",
    "performing", "performance", "residency", "stage", "show", "shows", "open", "days",
    "week", "weekend", "city", "town", "house", "centre", "center", "the", "of", "and", "for",
    # de
    "strasse", "strassen", "strassenfestival", "kunst", "kunstler", "kuenstler",
    "theaterfestival", "zirkusfestival", "kulturfestival", "festspiele", "internationales",
    "internationale", "tage", "woche", "haus", "und", "der", "die", "das",
    # fr
    "artistes", "rue", "rues", "spectacle", "spectacles", "fete", "des", "de", "du", "la",
    "le", "les", "et",
    # it / es
    "artisti", "artistidistrada", "strada", "strade", "teatro", "festa", "internazionale",
    "artistas", "calle", "internacional", "di", "del", "della", "y", "e",
    # nl
    "straat", "straattheater", "kunsten", "van", "het", "en",
}  # fmt: skip
NAME_TOKEN_MIN_LENGTH = 4

# Senders of web form confirmations. They never come from the organisation's own domain, so
# they are matched by name, or with the FORM fallback.
FORM_PROVIDER_DOMAINS = {
    "jotform.com",
    "formresponse.com",
    "typeform.com",
    "tally.so",
    "wufoo.com",
    "cognitoforms.com",
    "formstack.com",
    "123formbuilder.com",
    "paperform.co",
    "zohoforms.com",
    "wixforms.com",
    "submittable.com",
    "formspree.io",
    "fillout.com",
    "framaforms.org",
}
# Providers whose domain also sends other mail: only these exact addresses count.
FORM_PROVIDER_ADDRESSES = {
    "forms-receipts-noreply@google.com",
    "forms-noreply@google.com",
}


@dataclass
class Candidates:
    method: str
    applications: list[Application] = field(default_factory=list)
    organisations: list = field(default_factory=list)


def email_domain(address: str) -> str:
    return address.rsplit("@", 1)[-1].strip().lower() if "@" in address else ""


def normalise(text: str) -> str:
    return re.sub(r"[^\w]+", " ", text.lower()).strip()


def applications_for(organisations: Iterable, profile: Profile) -> list[Application]:
    """Not deleted applications of the profile to these organisations, newest first."""
    applications: list[Application] = []
    for organisation in organisations:
        content_type = ContentType.objects.get_for_model(organisation.__class__)
        applications += Application.objects.filter(
            profile=profile, content_type=content_type, object_id=organisation.id
        )
    return sorted(applications, key=lambda a: a.created_at, reverse=True)


def by_header(message: MailMessage) -> list[Application]:
    headers = " ".join(
        message.headers.get("in-reply-to", ()) + message.headers.get("references", ())
    )
    message_ids = re.findall(r"<[^<>\s]+>", headers)
    if not message_ids:
        return []
    return list(Application.objects.filter(sent_message_id__in=message_ids)[:1])


def by_sender(sender: str, profile: Profile) -> tuple[list[Application], list]:
    applications = [
        application
        for application in Application.objects.filter(profile=profile).exclude(
            email_recipients=None
        )
        if sender in {str(r).strip().lower() for r in application.email_recipients or []}
    ]
    organisations = [
        getattr(contact, model._meta.model_name)
        for model in ORGANISATION_MODELS
        for contact in model.contacts.rel.related_model.objects.filter(
            email__iexact=sender,
            **{f"{model._meta.model_name}__user": profile},
            **{f"{model._meta.model_name}__deleted_at__isnull": True},
        )
    ]
    return applications, organisations


def by_domain(domain: str, profile: Profile) -> list:
    if not domain or domain in FREE_MAIL_DOMAINS:
        return []
    organisations = []
    for model in ORGANISATION_MODELS:
        contact_model = model.contacts.rel.related_model
        name = model._meta.model_name
        org_ids = set(
            contact_model.objects.filter(
                email__iendswith=f"@{domain}", **{f"{name}__user": profile}
            ).values_list(name, flat=True)
        )
        for organisation in model.objects.filter(user=profile).exclude(website_url=""):
            if normalize_domain(organisation.website_url) == domain:
                org_ids.add(organisation.id)
        organisations += list(model.objects.filter(id__in=org_ids, user=profile))
    return organisations


def name_is_searchable(name: str) -> bool:
    name = normalise(name)
    return len(name) >= NAME_MIN_LENGTH and name not in GENERIC_NAMES


def fold(text: str) -> str:
    """normalise() without accents: "Fête" -> "fete"."""
    text = unicodedata.normalize("NFKD", normalise(text).replace("ß", "ss"))
    return "".join(c for c in text if not unicodedata.combining(c))


def distinctive_tokens(name: str) -> set[str]:
    """The words of an organisation name that identify it: "Ascona Street Festival" -> {"ascona"}."""
    return {
        token
        for token in fold(name).split()
        if len(token) >= NAME_TOKEN_MIN_LENGTH and token not in GENERIC_WORDS
    }


def names_in_text(items: list, name_of: Callable[[Any], str], text: str) -> list:
    """Items whose name is in the text. The whole name is searched first; only if nothing is
    found that way, an item matches when all the distinctive words of its name are in it."""
    phrase_text = f" {normalise(text)} "
    found = [
        item
        for item in items
        if name_is_searchable(name_of(item)) and f" {normalise(name_of(item))} " in phrase_text
    ]
    if found:
        return found
    words = set(fold(text).split())
    return [
        item for item in items if (tokens := distinctive_tokens(name_of(item))) and tokens <= words
    ]


def by_name(text: str, profile: Profile) -> list[Application]:
    """Recent applications (drafts included) whose organisation name appears in the text."""
    since = timezone.now() - timedelta(days=NAME_SEARCH_DAYS)
    applications = [
        application
        for application in Application.objects.filter(
            profile=profile, created_at__gte=since, object_id__isnull=False
        ).order_by("-created_at")
        if application.organisation is not None
    ]
    return names_in_text(applications, lambda a: a.organisation.name, text)


def organisations_by_name(text: str, profile: Profile) -> list:
    """The profile's festivals, venues and residencies whose name appears in the text."""
    organisations = [
        organisation
        for model in ORGANISATION_MODELS
        for organisation in model.objects.filter(user=profile, deleted_at__isnull=True).only(
            "id", "name"
        )
    ]
    return names_in_text(organisations, lambda o: o.name, text)


# "form" in the sender address (jotform, formresponse, forms-receipts...), but not in
# "information", "performance", "platform", "transform", "uniform", "reform", "formation"...
FORM_IN_ADDRESS = re.compile(r"(?<!in)(?<!per)(?<!plat)(?<!trans)(?<!uni)(?<!re)form(?!at)")


def is_form_provider(sender: str) -> bool:
    """Is the sender a web form service (Jotform, Typeform, Google Forms...)?"""
    sender = sender.strip().lower()
    domain = email_domain(sender)
    return (
        sender in FORM_PROVIDER_ADDRESSES
        or any(domain == p or domain.endswith(f".{p}") for p in FORM_PROVIDER_DOMAINS)
        or FORM_IN_ADDRESS.search(sender) is not None
    )


def find_candidates(message: MailMessage, profile: Optional[Profile]) -> Candidates:
    # Most robust matching: finds the application by the message ID we created
    applications = by_header(message)
    if applications:
        return Candidates("HEADER", applications)
    if profile is None:
        return Candidates("NONE")
    # Second screen: tries to find applications by matching SENDER with application.email_recipients and organisation.contacts
    sender = message.from_.strip().lower()
    applications, organisations = by_sender(sender, profile)
    applications = unique(applications + applications_for(organisations, profile))
    if applications or organisations:
        return Candidates("SENDER", applications, unique(organisations))

    # Third screen: tries to find applications by matching DOMAIN with application.email_recipients and organisation.contacts
    organisations = by_domain(email_domain(sender), profile)
    if organisations:
        return Candidates("DOMAIN", applications_for(organisations, profile), organisations)

    body = message.text or message.html or ""
    text = f"{message.subject}\n{body[:NAME_SEARCH_CHARS]}"

    # Web form confirmation: the artist applied on the organisation's website, so usually
    # there is no application yet. Find the organisation by name, so one can be created from
    # the email. Applications that already exist for it are still offered, to avoid duplicates.
    if is_form_provider(sender):
        organisations = organisations_by_name(text, profile)
        return Candidates("FORM", applications_for(organisations, profile), organisations)

    # Fourth screen: tries to find applications by matching subject or body with the organisation name
    applications = by_name(text, profile)
    if applications:
        return Candidates("NAME", applications)

    # No candidates found by programactic screening
    return Candidates("NONE")


def unique(items: list) -> list:
    seen = set()
    result = []
    for item in items:
        key = (item.__class__, item.pk)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result
