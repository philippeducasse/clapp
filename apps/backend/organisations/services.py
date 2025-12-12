import logging
from typing import Any, List, Optional

from django.utils import timezone

from applications.models import Application
from organisations.models import Organisation
from performances.models import Performance
from profiles.models import Profile

logger = logging.getLogger(__name__)


def generate_enrich_prompt(
    organisation: Organisation, search_results: Optional[str]
) -> str:
    """Generate enrichment prompt for any organisation type."""
    sr = search_results or "No search results provided."

    def nv(x: Any) -> str:
        return "" if x is None else str(x)

    # Format contacts for the prompt
    contacts_list = []
    for contact in organisation.contacts.all():
        contact_str = f"{contact.email}"
        if contact.name:
            contact_str = f"{contact.name} ({contact.email})"
        if contact.role:
            contact_str += f" - {contact.role}"
        contacts_list.append(contact_str)
    contacts_display = "; ".join(contacts_list) if contacts_list else "No contacts"

    prompt = f"""
    You are enriching organisation data for a cultural booking app.

    TASK
    - Read the current record and the web search snippets.
    - If the web snippets provide better or newer information for a field, **you must update it**.
    - If a field is missing in the snippets, keep the existing value.
    - Translate non-English data to English.
    - Normalize dates to ISO 8601 as strings: "YYYY-MM-DD".

    SOURCES & CONFLICTS
    - Prefer official organisation website > reputable cultural listings > news > blogs.
    - If sources conflict, pick the **most recent official source**.

    OUTPUT FORMAT
    - Return **only** a single JSON object, no prose.
    - Valid JSON. No comments. No trailing commas.
    - Exactly these keys (strings):
      country, town, website_url, description,
      contacts, sources, updated_fields
    - contacts should be an array of objects with: email (required), name (optional), role (optional).
      **IMPORTANT: Only include contacts if you find actual email addresses in the search results. 
      If no email addresses are found, return an empty array []. Do NOT invent or guess email addresses.**

    CURRENT RECORD
    country: {nv(organisation.country)}
    town: {nv(organisation.town)}
    website_url: {nv(organisation.website_url)}
    description: {nv(organisation.description)}
    contacts: {contacts_display}
    comments: {nv(organisation.comments)}

    WEB SEARCH SNIPPETS (include URLs if you have them)
    {sr}

    REQUIRED JSON SHAPE (example, syntactically correct — values are illustrative):
    {{
      "country": "Belgium",
      "town": "Brussels",
      "website_url": "https://example.be",
      "description": "A cultural organisation.",
      "contacts": [
        {{"email": "info@example.be"}},
        {{"email": "programming@example.be", "name": "John Smith", "role": "Programming Manager"}},
      ],
      "comments": "this is a comment."
    }}
    """
    return prompt


def generate_application_mail_prompt(
    organisation: Organisation,
    profile: Profile,
    performances: List[Performance],
    language: str,
) -> str:
    """Generate email application prompt for any organisation type."""
    print("LANGUAGE:", language)
    primary_contact = organisation.contacts.first()
    contact_name = None
    contact_emails = []

    if primary_contact:
        if primary_contact.name and primary_contact.name.strip().lower() != "nan":
            contact_name = primary_contact.name.strip()
        contact_emails = [c.email for c in organisation.contacts.all()]

    if contact_name:
        salutation = f"Use a standard salutation in {language} and include the name '{contact_name}'."
    else:
        salutation = f"Use a standard salutation using gender neutral language in {language} addressed to the {organisation.name} organizers."

    # Build artist identity section
    artist_identity = (
        f"{profile.first_name} {profile.last_name}".strip()
        or profile.artist_name
        or "the artist"
    )
    company_info = (
        f" representing {profile.company_name}" if profile.company_name else ""
    )

    # Build performances section with details
    if len(performances) == 1:
        performance = performances[0]
        performance_intro = f'your show "{performance.performance_title}"'
        performances_details = f"""
            Performance Details:
            - Title: {performance.performance_title}
            - Trailer: {performance.trailer if performance.trailer else "Not available"}
            - Type: {
            performance.get_performance_type_display()
            if performance.performance_type
            else "Not specified"
        }
            - Genres: {
            ", ".join([dict(Performance.GENRES).get(g, g) for g in performance.genres])
            if performance.genres
            else "Not specified"
        }
            - Duration: {performance.length if performance.length else "Not specified"}
            - Description: {
            performance.long_description
            if performance.long_description
            else "Not available"
        }
            - Dossier: {
            performance.dossiers.first()
            if performance.dossiers.exists()
            else "Not available"
        }
            """

        trailer_instruction = f'If the trailer is available ({performance.trailer}), add a link to it following this format: Here you can see the <a href="{performance.trailer}">trailer</a>, making sure the link is well separated from any other text and is clearly visible.'
        dossier_instruction = f"If a dossier is available ({performance.dossiers.first() if performance.dossiers.exists() else 'none'}), say that the dossier is attached and that all further information and photos are there."

    else:
        performance_intro = "your performances"
        performances_list = []
        trailers = []
        has_dossiers = False

        for perf in performances:
            perf_details = f"""
                * "{perf.performance_title}"
                    - Type: {
                perf.get_performance_type_display()
                if perf.performance_type
                else "Not specified"
            }
                    - Genres: {
                ", ".join([dict(Performance.GENRES).get(g, g) for g in perf.genres])
                if perf.genres
                else "Not specified"
            }
                    - Duration: {perf.length if perf.length else "Not specified"}
                    - Description: {
                perf.long_description if perf.long_description else "Not available"
            }
                    - Trailer: {perf.trailer if perf.trailer else "Not available"}
                    - Dossier: {
                perf.dossiers.first() if perf.dossiers.exists() else "Not available"
            }
                """
            performances_list.append(perf_details)

            if perf.trailer:
                trailers.append(
                    f'<a href="{perf.trailer}">{perf.performance_title} trailer</a>'
                )
            if perf.dossiers.exists():
                has_dossiers = True

        performances_details = "\nPerformances Details:" + "".join(performances_list)

        if trailers:
            trailer_instruction = f"Add links to the available trailers: {', '.join(trailers)}, making sure the links are well separated from any other text and clearly visible."
        else:
            trailer_instruction = "No trailers are available to link."

        if has_dossiers:
            dossier_instruction = "Say that the dossiers are attached and that all further information and photos are there."
        else:
            dossier_instruction = "No dossiers to mention."

    # Build contact information
    contact_lines = []
    if profile.email:
        contact_lines.append(f"<a href='mailto:{profile.email}'>{profile.email}</a>")
    if profile.personal_website:
        contact_lines.append(
            f"<a href='{profile.personal_website}'>{profile.personal_website}</a>"
        )

    # Build social media line
    social_links = []
    if profile.instagram_profile:
        social_links.append(f"<a href='{profile.instagram_profile}'>Instagram</a>")
    if profile.facebook_profile:
        social_links.append(f"<a href='{profile.facebook_profile}'>Facebook</a>")
    if profile.youtube_profile:
        social_links.append(f"<a href='{profile.youtube_profile}'>YouTube</a>")

    social_line = " & ".join(social_links) if social_links else ""

    # Format signature
    signature = f"{artist_identity}<br><br>"
    if profile.company_name:
        signature += f"{profile.company_name}<br>"
    if profile.phone:
        signature += f"{profile.phone}<br>"
    signature += "<br>".join(contact_lines)
    if social_line:
        signature += f"<br>{social_line}"

    # The full prompt
    prompt = f"""
        You are {artist_identity}{company_info}, a performer seeking to apply to various organisations with {performance_intro}.

        Generate ONLY the plain text email content (no additional messages) in {language}.
        IMPORTANT: Use the STANDARD written form of the language, NOT regional dialects or colloquial variations.
        Do not include a subject line.

        Artist Profile:
        - Name: {artist_identity}
        {f"- Company: {profile.company_name}" if profile.company_name else ""}
        {f"- Location: {profile.location}" if profile.location else ""}
        {f"- Nationality: {profile.nationality}" if profile.nationality else ""}
        {f"- Website: {profile.personal_website}" if profile.personal_website else ""}

        {performances_details}

        Organisation Details:
        - Name: {organisation.name}
        - Description: {organisation.description}
        - Contact Person: {contact_name if contact_name else "Not specified"}
        - Contact Emails: {", ".join(contact_emails) if contact_emails else "Not specified"}

        Email Requirements:
        - Salutation: {salutation}
        - Introduction: Briefly introduce yourself as {artist_identity} and mention your background. Then say that you would like to propose {performances} for the enxt edition of the event.
        - Body: Make the text very playful and informal. Explain why {performance_intro} {"is" if len(performances) == 1 else "are"} a great fit for this organisation, using the organisation description as your main reference.
        Mention unique aspects of the performance(s) and how {"it aligns" if len(performances) == 1 else "they align"} with the organisation's theme and audience.
        Use the performance details provided above to create a compelling pitch. Keep the body concise (max 500 characters).

        Example body:
            "Ah Bah Bravo! is a magical mix of world-class juggling — from butt and nose hooping to spinning a flaming staff with my feet while in a handstand!
            it's a show full of imagination, laughter, and wonder, perfectly suited to the lively and diverse spirit of your organisation.
            Audiences are invited to dream, share, and rediscover the carefree joy of being a child again".
        - Closing: {trailer_instruction} {dossier_instruction}
        Express enthusiasm in awaiting the response and openness to answer any questions or provide more information. Provide contact information using this format: {signature}

        Response Format Instructions:
        Return ONLY the email HTML content.
        CRITICAL: Use <br><br> tags for paragraph breaks (empty lines between sections).
        Use <a> tags for links.
        Do NOT use newlines, \\n characters, or any other line break methods.
        Do NOT use asterisks (* or **) for emphasis (*like this* or **like this**).
        Do not add any preamble message, notes, or formatting indicators.
        The response should begin immediately with the salutation.

        Email Structure (separate each section with <br><br>):
        1. Salutation (e.g., "Dear [Name],")
        2. Brief self-introduction (1-2 sentences about who you are)
        3. Main pitch about the performance(s) and organisation fit
        4. Closing with enthusiasm
        5. Sign-off (e.g., "Best regards," or equivalent in the target language)
        6. {signature}

        EXAMPLE OUTPUT FORMAT:

        Dear Team,<br><br>I am Philippe Ducasse, a circus artist based in Berlin with a passion for blending juggling, mime, and clowning into vibrant,
        family-friendly performances. I would like to propose my show "Ah Bah Bravo!" to the next edition of your festival.
        <br><br>"Ah Bah Bravo!" is a whirlwind of acrobatic butt hooping, flaming staff juggling while handstanding, and playful storytelling.
        It's a joyful celebration of childhood wonder, inviting audiences to laugh, dream, and embrace the magic of the moment.
        <br><br>Here you can see the <a href="https://example.com/trailer">trailer</a>
        <br><br>The dossier is attached with full details, photos, and technical requirements.
        Looking forward to your reply!
        <br><br>Best regards,<br><br>Philippe Ducasse<br>+4915203723753<br>info@philippeducasse.com<br>https://www.philippeducasse.com<br>Instagram & Facebook

        """
    return prompt.strip()


def create_form_application(
    organisation: Organisation,
    performances: List[Performance],
    default_profile: Profile,
    comments: str,
) -> Application:
    print("SO FAR SO GOOD")
    application = Application.objects.create(
        application_method="FORM",
        organisation=organisation,
        profile=default_profile,
        comments=comments,
        application_status="APPLIED",
        application_date=timezone.now().date(),
    )

    if performances:
        performance_ids = [
            int(id.strip()) for id in performances.split(",") if id.strip()
        ]
        application.performances.set(Performance.objects.filter(id__in=performance_ids))
        application.save()

    return application


def validate_application_recipients(recipients_input: str) -> List[str]:
    from django.core.exceptions import ValidationError
    from django.core.validators import validate_email

    recipient_emails = [
        email.strip() for email in recipients_input.split(",") if email.strip()
    ]

    if not recipient_emails:
        raise ValueError("At least one recipient email is required")

    try:
        for email in recipient_emails:
            validate_email(email)
    except ValidationError:
        raise ValueError(f"Invalid email address format: {recipient_emails}")

    return recipient_emails


def get_or_create_application(
    organisation: Organisation,
    profile: Profile,
    application_year: int,
    message: str,
    subject: str,
    recipient_emails: List[str],
) -> Application:
    from django.contrib.contenttypes.models import ContentType

    organisation_content_type = ContentType.objects.get_for_model(
        organisation.__class__
    )
    applications = Application.objects.filter(
        content_type=organisation_content_type, object_id=organisation.pk
    )

    application = next(
        (a for a in applications if a.application_year == application_year),
        None,
    )

    if application and "test" not in organisation.name.lower():
        if application.application_status != "DRAFT":
            raise ValueError(
                "Application already exists for this organisation and year"
            )
        else:
            application.message = message
            application.email_subject = subject
            application.save()
    else:
        application = Application.objects.create(
            organisation=organisation,
            application_date=timezone.now().date(),
            application_status="DRAFT",
            message=message,
            email_subject=subject,
            profile=profile,
            email_recipients=recipient_emails,
        )

    return application


def prepare_application_email(
    application: Application,
    recipient_emails: List[str],
    dossiers: Optional[str],
    attachments: List[Any],
    profile: Profile,
    performances: Optional[str],
) -> Any:
    """
    Prepare the application email with all attachments.
    """
    from django.core.mail import EmailMultiAlternatives
    from django.utils.html import strip_tags

    from performances.models import Dossier

    text_content = strip_tags(application.message)
    html_content = application.message

    email = EmailMultiAlternatives(
        application.email_subject,
        text_content,
        "info@philippeducasse.com",
        recipient_emails,
    )
    email.attach_alternative(html_content, "text/html")

    if dossiers:
        try:
            dossier_ids = [int(d) for d in dossiers.split(",")]
            logger.debug(f"Dossiers to send: {dossier_ids}")

        except ValueError:
            raise ValueError(f"Invalid dossier IDs: {dossiers}")

        if performances:
            performance_ids = [int(p) for p in performances.split(",")]
            dossier_objects = Dossier.objects.filter(
                id__in=dossier_ids,
                performance__profile=profile,
                performance__id__in=performance_ids,
            )
            logger.debug(f"Attaching dossiers: {dossier_objects}")

            for dossier in dossier_objects:
                with dossier.file.open("rb") as f:
                    email.attach(
                        dossier.name,
                        f.read(),
                        "application/pdf",
                    )

    for file in attachments:
        if hasattr(file, "content_type"):
            logger.debug(f"Attaching extra files: {file}")
            email.attach(file.name, file.read(), file.content_type)

    return email


def send_application_email(email: Any, application: Application) -> None:
    """
    Send the application email and update application status.
    """
    logger.debug(f"Sending email for application {application.id}")
    email.send(fail_silently=False)
    logger.debug("Email sent, updating application status to APPLIED")
    application.application_status = "APPLIED"
    application.save()
    logger.debug(f"Application {application.id} status updated")
