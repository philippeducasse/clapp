import logging
from email.utils import formataddr, make_msgid
from typing import Any, List, Optional

from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from applications.models import Application
from profiles.emails import get_user_email_connection
from profiles.models import Profile

logger = logging.getLogger(__name__)


def validate_application_recipients(recipients_input: str) -> List[str]:
    from django.core.exceptions import ValidationError
    from django.core.validators import validate_email

    recipient_emails = [email.strip() for email in recipients_input.split(",") if email.strip()]

    if not recipient_emails:
        raise ValueError("At least one recipient email is required")

    try:
        for email in recipient_emails:
            validate_email(email)
    except ValidationError:
        raise ValueError(f"Invalid email address format: {recipient_emails}")

    return recipient_emails



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
    from performances.models import Dossier

    text_content = strip_tags(application.message)
    html_content = application.message
    connection = get_user_email_connection(profile)
    try:
        logger.debug(
            f"Email connection: host={connection.host}, port={connection.port}, "
            f"user={connection.username}, tls={connection.use_tls}, ssl={connection.use_ssl}"
        )
    except AttributeError:
        # locmem backend doesn't have these attributes
        pass
    # SMTP credentials can differ from the address recipients should see.
    formatted_from_email = formataddr((profile.company_name, profile.email))

    email = EmailMultiAlternatives(
        application.email_subject,
        text_content,
        from_email=formatted_from_email,
        to=recipient_emails,
        connection=connection,
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
    # Skip email send if "test" is in recipient emails
    if application.email_recipients and any(
        "test" in recipient for recipient in application.email_recipients
    ):
        logger.info("Skipping email send in test mode")
        application.status = "APPLIED"
        application.save()
        return

    logger.debug(f"Sending email for application {application.id}")
    message_id = make_msgid(domain=application.profile.email.rsplit("@", 1)[-1])
    email.extra_headers["Message-ID"] = message_id
    email.send(fail_silently=False)
    logger.debug("Email sent, updating application status to APPLIED")
    application.email_id = message_id
    application.status = "APPLIED"
    application.save()
    logger.debug(f"Application {application.id} status updated")
