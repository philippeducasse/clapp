from django.core.mail import get_connection

from profiles.models import EMAIL_HOST_MAPPING, Profile


def get_user_email_connection(user: Profile):
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
