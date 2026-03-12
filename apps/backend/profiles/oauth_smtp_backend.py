import base64
import smtplib

from django.core.mail.backends.smtp import EmailBackend


class XOAuth2EmailBackend(EmailBackend):
    """SMTP backend that authenticates via XOAUTH2 instead of a password."""

    def __init__(self, access_token: str = "", **kwargs: str):
        kwargs.setdefault("password", "")
        super().__init__(**kwargs)
        self.access_token = access_token

    def open(self) -> bool:
        if self.connection:
            return False
        connection = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
        connection.ehlo()
        if self.use_tls:
            connection.starttls(context=self.ssl_context)
            connection.ehlo()
        auth_string = f"user={self.username}\x01auth=Bearer {self.access_token}\x01\x01"
        auth_bytes = base64.b64encode(auth_string.encode()).decode()
        connection.docmd("AUTH", f"XOAUTH2 {auth_bytes}")
        self.connection = connection
        return True
