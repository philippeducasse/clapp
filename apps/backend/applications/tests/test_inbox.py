from pathlib import Path
from unittest.mock import patch

import pytest
from imap_tools import MailMessage
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from applications.inbox import EmailClassification, check_inbox, import_email
from applications.models import Application, InboundEmail
from applications.services import set_application_status
from profiles.models import Profile

EMAILS = Path(__file__).parent / "emails"


def load(name: str) -> MailMessage:
    return MailMessage.from_bytes((EMAILS / name).read_bytes())


@pytest.fixture
def profile(db):
    return Profile.objects.create_user(email="info@philippeducasse.com", password="pw")


@pytest.fixture
def application(profile):
    return Application.objects.create(
        profile=profile,
        status="APPLIED",
        message="Dear organisers, I would like to propose my show.",
        sent_message_id="<sent-1@philippeducasse.com>",
    )


@pytest.fixture
def mock_llm():
    with patch("applications.inbox.classify") as classify:
        classify.return_value = EmailClassification(
            suggested_status="IN_DISCUSSION", summary="They want to talk about dates."
        )
        yield classify


@pytest.mark.django_db
class TestImportEmail:
    def test_reply_is_imported(self, application, mock_llm):
        email = import_email(load("reply.eml"))

        assert email.application == application
        assert email.from_address == "anna@festival-example.org"
        assert email.suggested_status == "IN_DISCUSSION"
        assert email.state == "PENDING_REVIEW"
        application.refresh_from_db()
        assert application.status == "APPLIED"

    def test_email_that_is_not_a_reply_is_ignored(self, application, mock_llm):
        assert import_email(load("unrelated.eml")) is None
        mock_llm.assert_not_called()

    def test_email_is_imported_once(self, application, mock_llm):
        import_email(load("reply.eml"))
        assert import_email(load("reply.eml")) is None
        assert InboundEmail.objects.count() == 1

    def test_check_inbox(self, application, mock_llm):
        with patch("applications.inbox.fetch_recent_emails") as fetch:
            fetch.return_value = [load("reply.eml"), load("unrelated.eml")]
            assert check_inbox() == 1


@pytest.mark.django_db
class TestSetApplicationStatus:
    def test_sets_status_and_adds_note(self, application):
        application.comments = "existing"
        set_application_status(application, "REJECTED", note="Programme full")
        application.refresh_from_db()
        assert application.status == "REJECTED"
        assert application.comments == "existing\nProgramme full"

    def test_invalid_status(self, application):
        with pytest.raises(ValidationError):
            set_application_status(application, "NOT_A_STATUS")


@pytest.mark.django_db
class TestInboundEmailApi:
    @pytest.fixture
    def client(self, profile):
        client = APIClient()
        client.force_authenticate(user=profile)
        return client

    @pytest.fixture
    def email(self, application, mock_llm):
        return import_email(load("reply.eml"))

    def test_list_only_shows_own_emails(self, client, email):
        other = Profile.objects.create_user(email="other@example.com", password="pw")
        other_app = Application.objects.create(profile=other, sent_message_id="<x@y>")
        InboundEmail.objects.create(application=other_app, message_id="<other@y>")

        response = client.get("/api/inbound-emails/?state=PENDING_REVIEW")
        assert [e["id"] for e in response.data["results"]] == [email.id]

    def test_filter_by_application(self, client, email, application, profile):
        other_app = Application.objects.create(profile=profile, sent_message_id="<z@y>")
        InboundEmail.objects.create(application=other_app, message_id="<other@y>")

        response = client.get(f"/api/inbound-emails/?application={application.id}")
        assert [e["id"] for e in response.data["results"]] == [email.id]

    def test_approve_uses_suggested_status(self, client, email, application):
        response = client.post(f"/api/inbound-emails/{email.id}/approve/")
        assert response.status_code == 200
        application.refresh_from_db()
        assert application.status == "IN_DISCUSSION"
        assert "talk about dates" in application.comments

    def test_approve_with_other_status(self, client, email, application):
        client.post(f"/api/inbound-emails/{email.id}/approve/", {"status": "ACCEPTED"})
        application.refresh_from_db()
        assert application.status == "ACCEPTED"

    def test_dismiss(self, client, email, application):
        client.post(f"/api/inbound-emails/{email.id}/dismiss/")
        email.refresh_from_db()
        application.refresh_from_db()
        assert email.state == "DISMISSED"
        assert application.status == "APPLIED"
