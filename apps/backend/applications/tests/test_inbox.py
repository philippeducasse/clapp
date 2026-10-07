from pathlib import Path
from unittest.mock import patch

import pytest
from django.contrib.contenttypes.models import ContentType
from imap_tools import MailMessage
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from applications.inbox import (
    EmailClassification,
    classify,
    check_inbox,
    import_email,
    is_auto_reply,
    is_skipped,
    mentions_keyword,
)
from applications.matching import Candidates
from applications.models import Application, InboundEmail
from organisations.festivals.models import Festival, FestivalContact
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
        classify.return_value = classification()
        yield classify


def classification(**kwargs) -> EmailClassification:
    return EmailClassification(
        **{
            "is_application_related": True,
            "application_id": None,
            "suggested_status": "IN_DISCUSSION",
            "is_auto_reply": False,
            "summary": "They want to talk about dates.",
            **kwargs,
        }
    )


def raw_email(sender: str, subject: str, body: str = "Hello") -> MailMessage:
    raw = f"From: {sender}\nSubject: {subject}\nMessage-ID: <{abs(hash(subject))}@x>\n"
    raw += 'Content-Type: text/plain; charset="utf-8"\n\n' + body
    return MailMessage.from_bytes(raw.encode())


@pytest.mark.django_db
class TestImportWithoutReplyHeaders:
    @pytest.fixture(autouse=True)
    def inbox_owner(self, monkeypatch, profile):
        monkeypatch.setenv("IMAP_USERNAME", profile.email)

    @pytest.fixture
    def festival(self, profile):
        festival = Festival.objects.create(name="Fringe Wonderland", user=profile)
        FestivalContact.objects.create(festival=festival, email="anna@fringe.org", user=profile)
        return festival

    @pytest.fixture
    def festival_application(self, festival, profile):
        return Application.objects.create(
            profile=profile,
            content_type=ContentType.objects.get_for_model(Festival),
            object_id=festival.id,
            status="DRAFT",
        )

    def test_llm_picks_a_candidate(self, festival_application, mock_llm):
        mock_llm.return_value = classification(
            application_id=festival_application.id, suggested_status="APPLIED"
        )
        email = import_email(raw_email("anna@fringe.org", "New thread"))

        assert email.application == festival_application
        assert email.suggested_status == "APPLIED"
        candidates = mock_llm.call_args.args[1]
        assert (candidates.method, candidates.applications) == ("SENDER", [festival_application])

    def test_llm_cannot_pick_an_application_that_is_not_a_candidate(
        self, festival_application, application, mock_llm
    ):
        mock_llm.return_value = classification(application_id=application.id)
        email = import_email(raw_email("anna@fringe.org", "New thread"))
        assert (email.state, email.application) == ("UNMATCHED", None)

    def test_no_candidate_chosen_is_unmatched(self, festival_application, profile, mock_llm):
        email = import_email(raw_email("anna@fringe.org", "New thread"))

        assert email.state == "UNMATCHED"
        assert email.application is None
        assert email.match_method == "NONE"
        assert email.profile == profile
        assert email.suggested_status == "IN_DISCUSSION"

    def test_organisation_without_application_is_kept(self, festival, mock_llm):
        email = import_email(raw_email("anna@fringe.org", "Would you play for us?"))
        assert (email.state, email.organisation) == ("UNMATCHED", festival)

    def test_not_application_related(self, festival_application, mock_llm):
        mock_llm.return_value = classification(
            application_id=festival_application.id, is_application_related=False
        )
        assert import_email(raw_email("anna@fringe.org", "Christmas party")) is None

    def test_no_candidates_and_no_keyword_skips_llm(self, mock_llm):
        assert import_email(raw_email("friend@gmail.com", "Dinner on Saturday?")) is None
        mock_llm.assert_not_called()

    def test_direct_enquiry_is_unmatched(self, mock_llm):
        email = import_email(raw_email("someone@newfest.org", "Invitation to our festival"))
        assert mock_llm.call_args.args[1].method == "NONE"
        assert (email.state, email.organisation) == ("UNMATCHED", None)

    def test_unmatched_needs_inbox_owner(self, monkeypatch, mock_llm):
        monkeypatch.setenv("IMAP_USERNAME", "nobody@example.com")
        assert import_email(raw_email("someone@newfest.org", "Invitation to our festival")) is None

    def test_match_method_and_auto_reply_are_saved(self, festival_application, mock_llm):
        mock_llm.return_value = classification(
            application_id=festival_application.id,
            suggested_status="AUTO_REPLY_RECEIVED",
            is_auto_reply=True,
        )
        email = import_email(raw_email("info@fringe.org", "Automatic reply"))
        assert email.match_method == "DOMAIN"
        assert email.is_auto_reply
        assert email.suggested_status == "AUTO_REPLY_RECEIVED"

    def test_header_match_ignores_llm_choice(self, application, festival_application, mock_llm):
        mock_llm.return_value = classification(
            application_id=festival_application.id, is_application_related=False
        )
        assert import_email(load("reply.eml")).application == application


@pytest.mark.django_db
def test_classify_prompt_lists_candidates(application):
    with patch("applications.inbox.MistralClient") as client:
        classify(load("reply.eml"), Candidates("HEADER", [application]))
        prompt = client.return_value.parse.call_args.args[0]
    assert f"- id: {application.id}" in prompt
    assert "I would like to propose my show" in prompt
    assert "From: Anna Booker <anna@festival-example.org>" in prompt


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


class TestPreFilter:
    def test_newsletter_is_skipped(self):
        assert is_skipped(load("newsletter.eml"))

    def test_reply_is_not_skipped(self):
        assert not is_skipped(load("reply.eml"))

    def test_auto_reply_is_not_skipped(self):
        message = load("auto_reply.eml")
        assert not is_skipped(message)
        assert is_auto_reply(message)

    def test_reply_is_not_auto_reply(self):
        assert not is_auto_reply(load("reply.eml"))

    @pytest.mark.parametrize("sender", ["MAILER-DAEMON@mx.example.org", "postmaster@example.org"])
    def test_bounce_is_skipped(self, sender):
        message = MailMessage.from_bytes(
            f"From: {sender}\nSubject: Undelivered\nMessage-ID: <b@x>\n\nBounce".encode()
        )
        assert is_skipped(message)

    def test_own_message_is_skipped(self, monkeypatch):
        monkeypatch.setenv("IMAP_USERNAME", "info@philippeducasse.com")
        message = MailMessage.from_bytes(
            b"From: Info@philippeducasse.com\nSubject: Hi\nMessage-ID: <o@x>\n\nHi"
        )
        assert is_skipped(message)


class TestMentionsKeyword:
    @staticmethod
    def message(subject: str, body: str = "") -> MailMessage:
        raw = f"From: x@y.org\nSubject: {subject}\nMessage-ID: <k@x>\n"
        raw += 'Content-Type: text/plain; charset="utf-8"\n\n' + body
        return MailMessage.from_bytes(raw.encode())

    @pytest.mark.parametrize(
        "subject, body",
        [
            ("Your show at our Festivals", ""),
            ("Hallo", "Danke für Ihre Bewerbung"),
            ("Anfrage Gastspiel 2027", ""),
            ("Bonjour", "Nous aimerions accueillir votre spectacle"),
            ("Votre candidature", ""),
            ("Re: Représentation", ""),  # accents are ignored
            ("Propuesta", "Nos encantaría su espectáculo"),
            ("Ciao", "Il vostro spettacolo"),
            ("Vraag", "Uw voorstelling"),
            ("Hi", "We would like to invite you to perform"),
        ],
    )
    def test_matches(self, subject, body):
        assert mentions_keyword(self.message(subject, body))

    @pytest.mark.parametrize(
        "subject, body",
        [
            ("Dinner on Saturday?", "Shall we meet at eight?"),
            ("Your invoice", "Thanks for your feedback, see attached."),
            ("Apple ID", "Your Apple account was updated"),
            ("Showerhead order", ""),
        ],
    )
    def test_does_not_match(self, subject, body):
        assert not mentions_keyword(self.message(subject, body))


@pytest.mark.django_db
class TestImportEmailPreFilter:
    def test_newsletter_is_not_imported(self, application, mock_llm):
        assert import_email(load("newsletter.eml")) is None
        mock_llm.assert_not_called()

    def test_auto_reply_is_imported(self, application, mock_llm):
        email = import_email(load("auto_reply.eml"))
        assert email.is_auto_reply  # from the headers, although the LLM said False
        assert email.match_method == "HEADER"
        assert email.profile == application.profile


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
        InboundEmail.objects.create(profile=other, application=other_app, message_id="<other@y>")

        response = client.get("/api/inbound-emails/?state=PENDING_REVIEW")
        assert [e["id"] for e in response.data["results"]] == [email.id]

    def test_filter_by_application(self, client, email, application, profile):
        other_app = Application.objects.create(profile=profile, sent_message_id="<z@y>")
        InboundEmail.objects.create(profile=profile, application=other_app, message_id="<other@y>")

        response = client.get(f"/api/inbound-emails/?application={application.id}")
        assert [e["id"] for e in response.data["results"]] == [email.id]

    def test_list_unmatched(self, client, email, profile):
        unmatched = InboundEmail.objects.create(
            profile=profile, message_id="<u@y>", state="UNMATCHED"
        )
        response = client.get("/api/inbound-emails/?state=UNMATCHED")
        assert [e["id"] for e in response.data["results"]] == [unmatched.id]
        assert response.data["results"][0]["application_status"] is None

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

    @pytest.fixture
    def unmatched(self, profile):
        festival = Festival.objects.create(name="New Fest", user=profile)
        return InboundEmail.objects.create(
            profile=profile,
            message_id="<u@y>",
            state="UNMATCHED",
            match_method="NONE",
            organisation=festival,
            suggested_status="IN_DISCUSSION",
            summary="They invite the show.",
        )

    def test_unmatched_shows_organisation(self, client, unmatched):
        data = client.get(f"/api/inbound-emails/{unmatched.id}/").data
        assert (data["organisation_name"], data["organisation_type"]) == ("New Fest", "festival")
        assert data["organisation_id"] == unmatched.organisation_id

    def test_approve_without_application(self, client, unmatched):
        response = client.post(f"/api/inbound-emails/{unmatched.id}/approve/")
        assert response.status_code == 400
        unmatched.refresh_from_db()
        assert unmatched.state == "UNMATCHED"

    def test_link(self, client, unmatched, application):
        response = client.post(
            f"/api/inbound-emails/{unmatched.id}/link/", {"application_id": application.id}
        )
        assert response.status_code == 200
        unmatched.refresh_from_db()
        application.refresh_from_db()
        assert (unmatched.state, unmatched.application) == ("PENDING_REVIEW", application)
        assert application.status == "APPLIED"

    def test_link_and_approve(self, client, unmatched, application):
        client.post(
            f"/api/inbound-emails/{unmatched.id}/link/",
            {"application_id": application.id, "approve": True},
            format="json",
        )
        unmatched.refresh_from_db()
        application.refresh_from_db()
        assert unmatched.state == "APPROVED"
        assert application.status == "IN_DISCUSSION"
        assert "They invite the show." in application.comments

    def test_link_corrects_a_wrong_match(self, client, email, profile):
        other = Application.objects.create(profile=profile, status="APPLIED")
        client.post(f"/api/inbound-emails/{email.id}/link/", {"application_id": other.id})
        email.refresh_from_db()
        assert email.application == other

    def test_link_to_another_users_application(self, client, unmatched):
        other = Profile.objects.create_user(email="other@example.com", password="pw")
        other_app = Application.objects.create(profile=other)
        response = client.post(
            f"/api/inbound-emails/{unmatched.id}/link/", {"application_id": other_app.id}
        )
        assert response.status_code == 400
        unmatched.refresh_from_db()
        assert unmatched.application is None

    def test_link_without_application_id(self, client, unmatched):
        assert client.post(f"/api/inbound-emails/{unmatched.id}/link/").status_code == 400
