from datetime import timedelta

import pytest
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from imap_tools import MailMessage

from applications.matching import (
    distinctive_tokens,
    find_candidates,
    is_form_provider,
    name_is_searchable,
)
from applications.models import Application
from organisations.festivals.models import Festival, FestivalContact
from organisations.venues.models import Venue
from profiles.models import Profile


def email(sender: str, subject: str = "Hello", body: str = "Hi", headers: str = "") -> MailMessage:
    raw = f"From: {sender}\nSubject: {subject}\nMessage-ID: <m@x>\n{headers}\n{body}"
    return MailMessage.from_bytes(raw.encode())


def apply_to(organisation, profile, **kwargs) -> Application:
    return Application.objects.create(
        profile=profile,
        content_type=ContentType.objects.get_for_model(organisation.__class__),
        object_id=organisation.id,
        **kwargs,
    )


@pytest.fixture
def profile(db):
    return Profile.objects.create_user(email="info@philippeducasse.com", password="pw")


@pytest.fixture
def festival(profile):
    festival = Festival.objects.create(
        name="Fringe Wonderland", website_url="https://www.fringe-wonderland.org/", user=profile
    )
    FestivalContact.objects.create(
        festival=festival, email="Anna@Fringe-Wonderland.org", user=profile
    )
    return festival


@pytest.fixture
def application(festival, profile):
    return apply_to(
        festival,
        profile,
        status="APPLIED",
        sent_message_id="<sent-1@philippeducasse.com>",
        email_recipients=["booking@other-domain.org"],
    )


@pytest.mark.django_db
class TestFindCandidates:
    def test_header(self, application, profile):
        message = email("someone@gmail.com", headers="In-Reply-To: <sent-1@philippeducasse.com>\n")
        result = find_candidates(message, profile)
        assert (result.method, result.applications) == ("HEADER", [application])

    def test_sender_is_a_contact(self, application, profile):
        result = find_candidates(email("anna@fringe-wonderland.org"), profile)
        assert (result.method, result.applications) == ("SENDER", [application])

    def test_sender_is_a_recipient(self, application, profile):
        result = find_candidates(email("Booking@Other-Domain.org"), profile)
        assert (result.method, result.applications) == ("SENDER", [application])

    def test_sender_contact_without_application(self, festival, profile):
        result = find_candidates(email("anna@fringe-wonderland.org"), profile)
        assert result.method == "SENDER"
        assert result.applications == []
        assert result.organisations == [festival]

    def test_domain_from_contact(self, application, profile):
        result = find_candidates(email("director@fringe-wonderland.org"), profile)
        assert (result.method, result.applications) == ("DOMAIN", [application])

    def test_domain_from_website(self, profile):
        venue = Venue.objects.create(name="Kulturhaus", website_url="kulturhaus.de", user=profile)
        result = find_candidates(email("info@kulturhaus.de"), profile)
        assert (result.method, result.organisations) == ("DOMAIN", [venue])

    def test_free_mail_domain_never_matches(self, profile):
        Festival.objects.create(name="Gmail Fest", website_url="https://gmail.com", user=profile)
        assert find_candidates(email("stranger@gmail.com"), profile).method == "NONE"

    def test_name_in_subject_includes_drafts(self, festival, profile):
        draft = apply_to(festival, profile, status="DRAFT")
        message = email(
            "noreply@mailer.example.com",
            subject="Your application to Fringe Wonderland was received",
        )
        result = find_candidates(message, profile)
        assert (result.method, result.applications) == ("NAME", [draft])

    def test_name_in_body(self, application, profile):
        message = email(
            "noreply@mailer.example.com", body="Thanks for applying to FRINGE-wonderland!"
        )
        assert find_candidates(message, profile).applications == [application]

    def test_name_must_be_a_whole_phrase(self, application, profile):
        message = email("noreply@mailer.example.com", body="The Fringe Wonderlands are great")
        assert find_candidates(message, profile).method == "NONE"

    def test_name_ignores_old_applications(self, application, profile):
        Application.objects.filter(pk=application.pk).update(
            created_at=timezone.now() - timedelta(days=400)
        )
        message = email("noreply@mailer.example.com", subject="Fringe Wonderland")
        assert find_candidates(message, profile).method == "NONE"

    def test_generic_name_never_matches(self, profile):
        apply_to(Festival.objects.create(name="Festival", user=profile), profile)
        message = email("noreply@mailer.example.com", subject="Our festival is great")
        assert find_candidates(message, profile).method == "NONE"

    def test_other_profiles_are_ignored(self, application):
        other = Profile.objects.create_user(email="other@example.com", password="pw")
        assert find_candidates(email("anna@fringe-wonderland.org"), other).method == "NONE"

    def test_deleted_application_is_ignored(self, application, profile):
        application.delete()
        result = find_candidates(email("anna@fringe-wonderland.org"), profile)
        assert result.applications == []


@pytest.mark.django_db
class TestNameTokens:
    @pytest.fixture
    def ascona(self, profile):
        festival = Festival.objects.create(name="Ascona Street Festival", user=profile)
        return apply_to(festival, profile, status="APPLIED", application_method="FORM")

    def test_distinctive_words_match(self, ascona, profile):
        message = email("news@mailer.example.com", subject='Ascona "Festival ArtistidiStrada"')
        result = find_candidates(message, profile)
        assert (result.method, result.applications) == ("NAME", [ascona])

    def test_all_distinctive_words_are_needed(self, profile):
        festival = Festival.objects.create(name="Festival Mondial du Cirque Vevey", user=profile)
        apply_to(festival, profile)
        message = email("noreply@other.com", subject="Vevey 2027")
        assert find_candidates(message, profile).method == "NONE"

    def test_accents_are_ignored(self, profile):
        festival = Festival.objects.create(name="Fête de Genève", user=profile)
        application = apply_to(festival, profile)
        message = email("noreply@other.com", subject="Inscription Geneve 2027")
        assert find_candidates(message, profile).applications == [application]

    def test_words_must_be_whole(self, ascona, profile):
        message = email("noreply@other.com", subject="Asconas rules")
        assert find_candidates(message, profile).method == "NONE"

    def test_generic_only_name_never_matches(self, profile):
        apply_to(Festival.objects.create(name="Street Festival", user=profile), profile)
        apply_to(
            Festival.objects.create(name="Festival des Artistes de Rue", user=profile), profile
        )
        message = email("noreply@other.com", subject="Artistes de rue: our festival in the street")
        assert find_candidates(message, profile).method == "NONE"

    def test_whole_name_match_wins(self, ascona, application, profile):
        message = email("noreply@other.com", subject="Fringe Wonderland and Ascona")
        assert find_candidates(message, profile).applications == [application]


@pytest.mark.django_db
class TestFormConfirmation:
    SUBJECT = 'Abbiamo ricevuto la tua risposta per Ascona "Festival ArtistidiStrada" 2027'

    @pytest.fixture
    def ascona(self, profile):
        return Festival.objects.create(name="Ascona Street Festival", user=profile)

    def form_email(self, subject: str = SUBJECT) -> MailMessage:
        return email("noreply@jotform.com", subject=subject)

    def test_finds_the_organisation_without_application(self, ascona, application, profile):
        result = find_candidates(self.form_email(), profile)
        assert (result.method, result.applications, result.organisations) == (
            "FORM",
            [],
            [ascona],
        )

    def test_existing_application_is_offered(self, ascona, profile):
        existing = apply_to(ascona, profile, status="APPLIED", application_method="FORM")
        result = find_candidates(self.form_email(), profile)
        assert (result.method, result.applications) == ("FORM", [existing])

    def test_whole_name_is_preferred(self, ascona, profile):
        festival = Festival.objects.create(name="Ascona Jazz", user=profile)
        result = find_candidates(self.form_email("Thanks for applying to Ascona Jazz"), profile)
        assert result.organisations == [festival]

    def test_unknown_organisation(self, profile):
        result = find_candidates(self.form_email("Pré-inscription Vevey 2027"), profile)
        assert (result.method, result.applications, result.organisations) == ("FORM", [], [])

    def test_deleted_and_other_users_organisations_are_ignored(self, ascona, profile):
        other = Profile.objects.create_user(email="other@example.com", password="pw")
        Festival.objects.create(name="Ascona Street Festival", user=other)
        ascona.deleted_at = timezone.now()
        ascona.save()
        assert find_candidates(self.form_email(), profile).organisations == []

    def test_known_contact_wins(self, festival, application, profile):
        FestivalContact.objects.create(festival=festival, email="forms@fringe.org", user=profile)
        result = find_candidates(email("forms@fringe.org"), profile)
        assert (result.method, result.applications) == ("SENDER", [application])


@pytest.mark.parametrize(
    "sender, expected",
    [
        ("noreply@jotform.com", True),
        ("NoReply@Mail.Jotform.com", True),
        ("forms-receipts-noreply@google.com", True),
        ("noreply@formresponse.com", True),
        ("submissions@myforms.example.org", True),
        ("no-reply@accounts.google.com", False),
        ("anna@festival.org", False),
        ("information@festival.org", False),
        ("booking@performance-fest.org", False),
        ("formation@cirque.fr", False),
        ("noreply@platform.io", False),
    ],
)
def test_is_form_provider(sender, expected):
    assert is_form_provider(sender) is expected


@pytest.mark.parametrize(
    "name, tokens",
    [
        ("Ascona Street Festival", {"ascona"}),
        ("Festival International des Artistes de Rue de Vevey", {"vevey"}),
        ("Straßenfestival Bümpliz", {"bumpliz"}),
        ("Street Festival", set()),
        ("Fest Rue", set()),
    ],
)
def test_distinctive_tokens(name, tokens):
    assert distinctive_tokens(name) == tokens


@pytest.mark.parametrize(
    "name, searchable", [("Fringe Wonderland", True), ("Festival", False), ("Kult", False)]
)
def test_name_is_searchable(name, searchable):
    assert name_is_searchable(name) is searchable
