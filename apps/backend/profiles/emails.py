from django.core.mail import get_connection


def get_user_email_connection(user):
    return get_connection(
        backend="django.core.mail.backends.smtp.EmailBackend",
        host=user.email_host,
        port=user.email_port,
        username=user.email_host_user,
        password=user.email_host_password,
        use_tls=user.email_use_tls,
    )
