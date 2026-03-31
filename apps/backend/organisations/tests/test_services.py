"""Tests for organisations/services.py."""

from unittest.mock import MagicMock

import pytest
from django.utils import timezone

from applications.models import Application
from organisations.festivals.models import Festival, FestivalContact
from organisations.services import (
    _format_contacts_for_prompt,
    create_form_application,
    format_email,
    generate_application_mail_prompt,
    generate_enrich_prompt,
    parse_performance_ids,
    send_application_email,
    validate_application_recipients,
)
from performances.models import Performance
from profiles.models import Profile


@pytest.mark.django_db
class TestFormatContactsForPrompt:
    def test_no_contacts(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Test Fest", town="Paris", country="France", user=profile
        )
        result = _format_contacts_for_prompt(festival)
        assert result == "No contacts"

    def test_with_contact_email_only(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Test Fest", town="Paris", country="France", user=profile
        )
        FestivalContact.objects.create(festival=festival, email="info@fest.com", user=profile)
        result = _format_contacts_for_prompt(festival)
        assert "info@fest.com" in result

    def test_with_contact_name_and_role(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Test Fest", town="Paris", country="France", user=profile
        )
        FestivalContact.objects.create(
            festival=festival, email="info@fest.com", name="Alice", role="Director", user=profile
        )
        result = _format_contacts_for_prompt(festival)
        assert "Alice" in result
        assert "Director" in result


@pytest.mark.django_db
class TestGenerateEnrichPrompt:
    def test_returns_string_prompt(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Test Fest", town="Paris", country="France", user=profile
        )
        prompt = generate_enrich_prompt(festival, "some search results")
        assert isinstance(prompt, str)
        assert "France" in prompt
        assert "Paris" in prompt

    def test_with_no_search_results(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Test Fest", town="Paris", country="France", user=profile
        )
        prompt = generate_enrich_prompt(festival, None)
        assert isinstance(prompt, str)
        assert "No search results" in prompt

    def test_with_contacts(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Test Fest", town="Paris", country="France", user=profile
        )
        FestivalContact.objects.create(
            festival=festival, email="contact@fest.com", name="Bob", role="Manager", user=profile
        )
        prompt = generate_enrich_prompt(festival, "results")
        assert "Bob" in prompt or "contact@fest.com" in prompt


@pytest.mark.django_db
class TestGenerateApplicationMailPrompt:
    def test_single_performance(self):
        profile = Profile.objects.create_user(
            email="t@example.com", password="pass", company_name="Cool Company"
        )
        festival = Festival.objects.create(
            name="Mail Fest", town="Paris", country="France", user=profile
        )
        performance = Performance.objects.create(
            profile=profile,
            performance_title="My Show",
            short_description="A great show",
        )
        prompt = generate_application_mail_prompt(festival, profile, [performance], "ENGLISH", 3)
        assert isinstance(prompt, str)
        assert "My Show" in prompt

    def test_multiple_performances(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Mail Fest", town="Paris", country="France", user=profile
        )
        p1 = Performance.objects.create(
            profile=profile, performance_title="Show A", short_description="desc"
        )
        p2 = Performance.objects.create(
            profile=profile, performance_title="Show B", short_description="desc"
        )
        prompt = generate_application_mail_prompt(festival, profile, [p1, p2], "FRENCH", 2)
        assert isinstance(prompt, str)
        assert "Show A" in prompt
        assert "Show B" in prompt

    def test_with_contact_name(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Mail Fest", town="Paris", country="France", user=profile
        )
        FestivalContact.objects.create(
            festival=festival, email="contact@fest.com", name="John Smith", user=profile
        )
        performance = Performance.objects.create(
            profile=profile, performance_title="My Show", short_description="desc"
        )
        prompt = generate_application_mail_prompt(festival, profile, [performance], "ENGLISH", 1)
        assert "John Smith" in prompt

    def test_with_trailer_and_dossier(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Mail Fest", town="Paris", country="France", user=profile
        )
        performance = Performance.objects.create(
            profile=profile,
            performance_title="My Show",
            short_description="desc",
            trailer="https://youtube.com/watch?v=123",
        )
        prompt = generate_application_mail_prompt(festival, profile, [performance], "ENGLISH", 4)
        assert "youtube.com" in prompt

    def test_with_multiple_trailers(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Mail Fest", town="Paris", country="France", user=profile
        )
        p1 = Performance.objects.create(
            profile=profile,
            performance_title="Show A",
            short_description="desc",
            trailer="https://youtube.com/1",
        )
        p2 = Performance.objects.create(
            profile=profile,
            performance_title="Show B",
            short_description="desc",
        )
        prompt = generate_application_mail_prompt(festival, profile, [p1, p2], "ENGLISH", 5)
        assert "Show A" in prompt

    def test_with_default_length(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Mail Fest", town="Paris", country="France", user=profile
        )
        performance = Performance.objects.create(
            profile=profile, performance_title="My Show", short_description="desc"
        )
        # length=None should use default (3)
        prompt = generate_application_mail_prompt(festival, profile, [performance], "ENGLISH", None)
        assert isinstance(prompt, str)


class TestFormatEmail:
    def test_replaces_newlines_with_br(self):
        result = format_email("Hello\nWorld")
        assert result == "Hello<br>World"

    def test_removes_asterisks(self):
        result = format_email("**bold** and *italic*")
        assert result == "bold and italic"


@pytest.mark.django_db
class TestCreateFormApplication:
    def test_creates_application_with_performances(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Form Fest", town="Paris", country="France", user=profile
        )
        performance = Performance.objects.create(
            profile=profile, performance_title="Show", short_description="desc"
        )
        app = create_form_application(festival, [performance], profile, "Some comments")
        assert app.id is not None
        assert app.application_method == "FORM"
        assert app.status == "APPLIED"
        assert app.performances.count() == 1

    def test_creates_application_without_performances(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Form Fest", town="Paris", country="France", user=profile
        )
        app = create_form_application(festival, [], profile, "")
        assert app.id is not None
        assert app.performances.count() == 0


@pytest.mark.django_db
class TestValidateApplicationRecipients:
    def test_valid_single_email(self):
        emails = validate_application_recipients("contact@example.com")
        assert emails == ["contact@example.com"]

    def test_valid_multiple_emails(self):
        emails = validate_application_recipients("a@example.com, b@example.com")
        assert len(emails) == 2

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="At least one recipient"):
            validate_application_recipients("")

    def test_invalid_email_raises(self):
        with pytest.raises(ValueError, match="Invalid email"):
            validate_application_recipients("not-an-email")


@pytest.mark.django_db
class TestParsePerformanceIds:
    def test_empty_returns_empty_list(self):
        result = parse_performance_ids(None)
        assert result == []

    def test_string_ids(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        p = Performance.objects.create(profile=profile, performance_title="Show")
        result = parse_performance_ids(str(p.id))
        assert len(result) == 1
        assert result[0].id == p.id

    def test_list_ids(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        p = Performance.objects.create(profile=profile, performance_title="Show")
        result = parse_performance_ids([p.id])
        assert len(result) == 1

    def test_single_int_id(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        p = Performance.objects.create(profile=profile, performance_title="Show")
        result = parse_performance_ids(p.id)
        assert len(result) == 1

    def test_nonexistent_id_returns_empty(self):
        result = parse_performance_ids(99999)
        assert result == []


@pytest.mark.django_db
class TestSendApplicationEmail:
    def test_test_recipient_skips_send(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Send Fest", town="Paris", country="France", user=profile
        )
        app = Application.objects.create(
            organisation=festival,
            profile=profile,
            status="DRAFT",
            application_date=timezone.now().date(),
            email_recipients=["test@example.com"],
        )
        mock_email = MagicMock()
        send_application_email(mock_email, app)
        mock_email.send.assert_not_called()
        app.refresh_from_db()
        assert app.status == "APPLIED"

    def test_real_recipient_sends_email(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Send Fest", town="Paris", country="France", user=profile
        )
        app = Application.objects.create(
            organisation=festival,
            profile=profile,
            status="DRAFT",
            application_date=timezone.now().date(),
            email_recipients=["contact@festival.com"],
        )
        mock_email = MagicMock()
        send_application_email(mock_email, app)
        mock_email.send.assert_called_once()
        app.refresh_from_db()
        assert app.status == "APPLIED"
