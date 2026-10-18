from datetime import timedelta
from unittest.mock import patch

import httpx
import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from discovery.models import DiscoveryCandidate, DiscoveryRun, DiscoverySource
from organisations.festivals.models import Festival, FestivalContact
from organisations.residencies.models import Residency
from organisations.venues.models import Venue
from profiles.models import Profile

TOKEN = "test-service-token"


@pytest.fixture(autouse=True)
def service_settings(settings):
    settings.DISCOVERY_SERVICE_TOKEN = TOKEN
    settings.DISCOVERY_SERVICE_URL = "http://discovery.test"


@pytest.fixture
def superuser(db):
    return Profile.objects.create_superuser(email="admin@example.com", password="pass")


@pytest.fixture
def user(db):
    return Profile.objects.create_user(email="user@example.com", password="pass")


@pytest.fixture
def admin_client(superuser):
    client = APIClient()
    client.force_authenticate(user=superuser)
    return client


@pytest.fixture
def service_client():
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {TOKEN}")
    return client


@pytest.fixture
def service_ok():
    """The discovery service accepts the run."""
    with patch(
        "discovery.service_client.httpx.post",
        return_value=httpx.Response(202, json={"accepted": True}),
    ) as mock_post:
        yield mock_post


def make_candidate(**fields) -> DiscoveryCandidate:
    defaults = {
        "org_type": DiscoveryCandidate.OrgType.FESTIVAL,
        "name": "Found Fest",
        "country": "Belgium",
        "town": "Ghent",
        "website_url": "https://foundfest.be",
        "domain": "foundfest.be",
    }
    return DiscoveryCandidate.objects.create(**{**defaults, **fields})


# --- Access ------------------------------------------------------------------------------


@pytest.mark.django_db
class TestAccess:
    @pytest.mark.parametrize(
        "method, url",
        [
            ("get", "/api/discovery/runs/"),
            ("post", "/api/discovery/runs/"),
            ("get", "/api/discovery/candidates/"),
        ],
    )
    @pytest.mark.parametrize("kind", ["user", "staff"])
    def test_non_superusers_are_forbidden(self, method, url, kind):
        profile = Profile.objects.create_user(
            email=f"{kind}@example.com", password="pass", is_staff=kind == "staff"
        )
        client = APIClient()
        client.force_authenticate(user=profile)

        response = getattr(client, method)(url, {"starting_point": "x"}, format="json")

        assert response.status_code == 403

    def test_non_superuser_cannot_accept(self, user):
        candidate = make_candidate()
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(f"/api/discovery/candidates/{candidate.id}/accept/")

        assert response.status_code == 403
        assert not Festival.objects.filter(name="Found Fest", user__isnull=True).exists()

    def test_anonymous_is_rejected(self, db):
        assert APIClient().get("/api/discovery/runs/").status_code == 403

    @pytest.mark.parametrize(
        "header",
        [None, "Bearer wrong-token", f"Token {TOKEN}", "Bearer "],
    )
    def test_internal_api_requires_service_token(self, db, header):
        client = APIClient()
        if header is not None:
            client.credentials(HTTP_AUTHORIZATION=header)

        response = client.get("/internal/discovery/known-index/")

        assert response.status_code == 401

    def test_internal_api_rejects_superuser_session(self, superuser):
        client = APIClient()
        client.force_login(superuser)  # a real session cookie, which the internal API ignores

        assert client.get("/internal/discovery/known-index/").status_code == 401

    def test_internal_api_rejects_everything_when_no_token_configured(self, settings, db):
        settings.DISCOVERY_SERVICE_TOKEN = ""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer ")

        assert client.get("/internal/discovery/known-index/").status_code == 401

    def test_internal_post_needs_no_csrf_token(self, db):
        """The service has no session or CSRF cookie; the bearer token is enough."""
        client = APIClient(enforce_csrf_checks=True)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {TOKEN}")

        response = client.post("/internal/discovery/sources/", {"sources": []}, format="json")

        assert response.status_code == 200


# --- Runs (frontend API) -----------------------------------------------------------------


@pytest.mark.django_db
class TestRuns:
    def test_create_starts_run_on_service(self, admin_client, superuser, service_ok):
        response = admin_client.post(
            "/api/discovery/runs/",
            {"starting_point": "  https://some-juggler.com  "},
            format="json",
        )

        assert response.status_code == 201
        run = DiscoveryRun.objects.get()
        assert run.status == DiscoveryRun.Status.QUEUED
        assert run.starting_point == "https://some-juggler.com"
        assert run.created_by == superuser
        assert response.data["is_active"] is True
        args, kwargs = service_ok.call_args
        assert args[0] == "http://discovery.test/runs"
        assert kwargs["json"] == {"run_id": run.id, "starting_point": run.starting_point}
        assert kwargs["headers"] == {"Authorization": f"Bearer {TOKEN}"}

    @pytest.mark.parametrize(
        "side_effect, return_value",
        [
            (httpx.ConnectError("refused"), None),
            (None, httpx.Response(409, text="busy")),
        ],
    )
    def test_service_failure_marks_run_failed(self, admin_client, side_effect, return_value):
        with patch(
            "discovery.service_client.httpx.post",
            side_effect=side_effect,
            return_value=return_value,
        ):
            response = admin_client.post(
                "/api/discovery/runs/", {"starting_point": "festivals"}, format="json"
            )

        assert response.status_code == 201
        assert response.data["status"] == "FAILED"
        assert response.data["error"]
        assert DiscoveryRun.objects.get().finished_at is not None

    def test_only_one_active_run(self, admin_client, service_ok):
        first = admin_client.post("/api/discovery/runs/", {"starting_point": "a"}, format="json")
        second = admin_client.post("/api/discovery/runs/", {"starting_point": "b"}, format="json")

        assert second.status_code == 409
        assert second.data["run_id"] == first.data["id"]
        assert DiscoveryRun.objects.count() == 1
        assert service_ok.call_count == 1

    @pytest.mark.parametrize("value", ["", "   ", "x" * 2001])
    def test_invalid_starting_point(self, admin_client, service_ok, value):
        response = admin_client.post(
            "/api/discovery/runs/", {"starting_point": value}, format="json"
        )

        assert response.status_code == 400
        service_ok.assert_not_called()

    def test_stale_run_is_failed_when_read_and_no_longer_blocks(self, admin_client, service_ok):
        stale = DiscoveryRun.objects.create(
            starting_point="old",
            status=DiscoveryRun.Status.RUNNING,
            last_heartbeat_at=timezone.now() - timedelta(minutes=11),
        )

        detail = admin_client.get(f"/api/discovery/runs/{stale.id}/")
        assert detail.data["status"] == "FAILED"
        assert "10 minutes" in detail.data["error"]

        response = admin_client.post(
            "/api/discovery/runs/", {"starting_point": "new"}, format="json"
        )
        assert response.status_code == 201

    def test_recent_heartbeat_keeps_run_active(self, admin_client):
        run = DiscoveryRun.objects.create(
            starting_point="x",
            status=DiscoveryRun.Status.RUNNING,
            last_heartbeat_at=timezone.now() - timedelta(minutes=2),
        )

        assert admin_client.get(f"/api/discovery/runs/{run.id}/").data["status"] == "RUNNING"

    def test_queued_run_without_heartbeat_expires_from_created_at(self, admin_client):
        run = DiscoveryRun.objects.create(starting_point="x")
        DiscoveryRun.objects.filter(pk=run.pk).update(
            created_at=timezone.now() - timedelta(minutes=11)
        )

        admin_client.get("/api/discovery/runs/")

        run.refresh_from_db()
        assert run.status == DiscoveryRun.Status.FAILED

    def test_cancel(self, admin_client):
        run = DiscoveryRun.objects.create(
            starting_point="x", status=DiscoveryRun.Status.RUNNING, last_heartbeat_at=timezone.now()
        )

        response = admin_client.post(f"/api/discovery/runs/{run.id}/cancel/")

        assert response.status_code == 200
        assert response.data["cancel_requested"] is True

    def test_cannot_cancel_finished_run(self, admin_client):
        run = DiscoveryRun.objects.create(starting_point="x", status=DiscoveryRun.Status.DONE)

        assert admin_client.post(f"/api/discovery/runs/{run.id}/cancel/").status_code == 400


# --- Run updates (internal API) ----------------------------------------------------------


@pytest.mark.django_db
class TestRunUpdates:
    def _run(self, **fields):
        return DiscoveryRun.objects.create(starting_point="x", **fields)

    def test_running_then_done(self, service_client):
        run = self._run()

        response = service_client.patch(
            f"/internal/discovery/runs/{run.id}/",
            {
                "status": "RUNNING",
                "plan": {"goal": "find festivals"},
                "counters": {"pages": 3},
                "progress": [{"step": "search", "message": "Searching"}],
                "errors": ["timeout on a.com"],
            },
            format="json",
        )

        assert response.status_code == 200
        assert response.data == {"status": "RUNNING", "cancel_requested": False}
        run.refresh_from_db()
        assert run.started_at is not None
        assert run.last_heartbeat_at is not None
        assert run.plan == {"goal": "find festivals"}
        assert run.progress[0]["step"] == "search"
        assert run.progress[0]["at"]
        assert run.errors == ["timeout on a.com"]

        service_client.patch(
            f"/internal/discovery/runs/{run.id}/",
            {
                "status": "DONE",
                "counters": {"pages": 9, "candidates": 2},
                "progress": [{"step": "save", "message": "Saved 2 candidates"}],
                "errors": ["dns error on b.com"],
            },
            format="json",
        )

        run.refresh_from_db()
        assert run.status == "DONE"
        assert run.finished_at is not None
        assert run.counters == {"pages": 9, "candidates": 2}  # replaced
        assert [line["step"] for line in run.progress] == ["search", "save"]  # appended
        assert run.errors == ["timeout on a.com", "dns error on b.com"]  # appended

    def test_reports_cancel_request(self, service_client):
        run = self._run(status=DiscoveryRun.Status.RUNNING, cancel_requested=True)

        response = service_client.patch(
            f"/internal/discovery/runs/{run.id}/",
            {"progress": [{"step": "visit", "message": "…"}]},
            format="json",
        )

        assert response.data["cancel_requested"] is True

    def test_finished_run_is_never_reopened(self, service_client):
        run = self._run(status=DiscoveryRun.Status.FAILED)

        response = service_client.patch(
            f"/internal/discovery/runs/{run.id}/", {"status": "RUNNING"}, format="json"
        )

        assert response.data == {"status": "FAILED", "cancel_requested": True}
        run.refresh_from_db()
        assert run.status == "FAILED"

    def test_progress_is_capped(self, service_client):
        run = self._run(status=DiscoveryRun.Status.RUNNING)
        run.progress = [{"at": "", "step": "old", "message": str(i)} for i in range(499)]
        run.save()

        service_client.patch(
            f"/internal/discovery/runs/{run.id}/",
            {"progress": [{"step": "new", "message": "a"}, {"step": "new", "message": "b"}]},
            format="json",
        )

        run.refresh_from_db()
        assert len(run.progress) == DiscoveryRun.MAX_PROGRESS_LINES
        assert run.progress[-1]["message"] == "b"
        assert run.progress[0]["message"] == "1"

    @pytest.mark.parametrize("status_value", ["QUEUED", "BOGUS"])
    def test_invalid_status(self, service_client, status_value):
        run = self._run()

        response = service_client.patch(
            f"/internal/discovery/runs/{run.id}/", {"status": status_value}, format="json"
        )

        assert response.status_code == 400

    def test_unknown_run(self, service_client):
        response = service_client.patch("/internal/discovery/runs/999/", {}, format="json")

        assert response.status_code == 404


# --- Known index and saving candidates (internal API) ------------------------------------


@pytest.mark.django_db
class TestKnownIndex:
    def test_contents(self, service_client, superuser, user):
        staff = Profile.objects.create_user(email="staff@example.com", password="p", is_staff=True)
        Festival.objects.create(
            user=None, name="Seed Fest", country="France", website_url="https://www.seed.fr/x"
        )
        Venue.objects.create(user=superuser, name="Admin Hall", country="Italy")
        Residency.objects.create(user=user, name="Private Res")
        Residency.objects.create(user=staff, name="Staff Res")
        deleted = Festival.objects.create(user=None, name="Gone Fest")
        deleted.delete()
        make_candidate(name="Old Candidate", state=DiscoveryCandidate.State.DISMISSED)

        response = service_client.get("/internal/discovery/known-index/")

        assert response.status_code == 200
        by_name = {entry["name"]: entry for entry in response.data}
        # The superuser and the plain user also got clones of "Seed Fest" at signup;
        # only the seed itself and the superuser's own rows count as shared knowledge.
        assert by_name["Seed Fest"]["domain"] == "seed.fr"
        assert by_name["Seed Fest"]["org_type"] == "FESTIVAL"
        assert by_name["Admin Hall"]["source"] == "SUPERUSER"
        assert by_name["Old Candidate"]["source"] == "CANDIDATE"
        assert "Private Res" not in by_name
        assert "Staff Res" not in by_name
        assert "Gone Fest" not in by_name


@pytest.mark.django_db
class TestCreateCandidates:
    def _post(self, client, run, candidates):
        return client.post(
            f"/internal/discovery/runs/{run.id}/candidates/",
            {"candidates": candidates},
            format="json",
        )

    def test_saves_candidates(self, service_client):
        run = DiscoveryRun.objects.create(starting_point="x", status="RUNNING")

        response = self._post(
            service_client,
            run,
            [
                {
                    "org_type": "FESTIVAL",
                    "name": "New Fest",
                    "country": "Belgium",
                    "website_url": "https://www.newfest.be/en",
                    "contacts": [{"name": "Ana", "email": "ana@newfest.be"}],
                    "found_via": [{"kind": "ARTIST_SITE", "url": "https://juggler.com/tour"}],
                    "sources": [{"url": "https://newfest.be/contact", "snippet": "ana@newfest.be"}],
                    "relevance_reason": "A peer artist played here in 2025.",
                },
                {"org_type": "RESIDENCY", "name": "Lost Res", "state": "UNRESOLVED"},
            ],
        )

        assert response.status_code == 201
        assert response.data == {"created": 2, "already_known": 0}
        fest = DiscoveryCandidate.objects.get(name="New Fest")
        assert fest.run == run
        assert fest.domain == "newfest.be"
        assert fest.state == "PENDING"
        assert fest.contacts == [{"name": "Ana", "email": "ana@newfest.be", "role": ""}]
        assert DiscoveryCandidate.objects.get(name="Lost Res").state == "UNRESOLVED"

    def test_exact_matches_become_already_known(self, service_client):
        Festival.objects.create(
            user=None, name="Seed Fest", country="France", website_url="https://seed.fr"
        )
        make_candidate(name="Earlier", website_url="https://earlier.be", domain="earlier.be")
        run = DiscoveryRun.objects.create(starting_point="x")

        response = self._post(
            service_client,
            run,
            [
                {
                    "org_type": "FESTIVAL",
                    "name": "Other name",
                    "website_url": "http://www.seed.fr/",
                },
                {"org_type": "FESTIVAL", "name": "seed fest", "country": "FRANCE"},
                {
                    "org_type": "FESTIVAL",
                    "name": "Earlier again",
                    "website_url": "https://earlier.be",
                },
                {"org_type": "FESTIVAL", "name": "Twice", "website_url": "https://twice.be"},
                {"org_type": "FESTIVAL", "name": "Twice", "website_url": "https://twice.be"},
                {"org_type": "FESTIVAL", "name": "Seed Fest", "country": "Spain"},
            ],
        )

        assert response.data == {"created": 2, "already_known": 4}
        states = list(
            DiscoveryCandidate.objects.filter(run=run)
            .order_by("id")
            .values_list("state", flat=True)
        )
        assert states == [
            "ALREADY_KNOWN",
            "ALREADY_KNOWN",
            "ALREADY_KNOWN",
            "PENDING",
            "ALREADY_KNOWN",
            "PENDING",
        ]

    @pytest.mark.parametrize(
        "candidate",
        [
            {"org_type": "FESTIVAL", "name": "X", "state": "ACCEPTED"},
            {"org_type": "CIRCUS", "name": "X"},
            {"org_type": "FESTIVAL", "name": ""},
            {"org_type": "FESTIVAL", "name": "X", "contacts": [{"email": "not-an-email"}]},
            {"org_type": "FESTIVAL", "name": "X", "website_url": "not a url"},
        ],
    )
    def test_invalid_candidates_rejected(self, service_client, candidate):
        run = DiscoveryRun.objects.create(starting_point="x")

        response = self._post(service_client, run, [candidate])

        assert response.status_code == 400
        assert not DiscoveryCandidate.objects.exists()

    def test_unknown_run(self, service_client):
        response = service_client.post(
            "/internal/discovery/runs/999/candidates/", {"candidates": []}, format="json"
        )

        assert response.status_code == 404


@pytest.mark.django_db
class TestSources:
    def test_upsert_adds_leads(self, service_client):
        body = {
            "sources": [
                {
                    "url": "https://www.juggler.com/",
                    "kind": "ARTIST_SITE",
                    "calendar_url": "https://www.juggler.com/tour",
                    "leads_found": 4,
                }
            ]
        }
        service_client.post("/internal/discovery/sources/", body, format="json")
        body["sources"][0].update(leads_found=2, calendar_url="")
        response = service_client.post("/internal/discovery/sources/", body, format="json")

        assert response.status_code == 200
        source = DiscoverySource.objects.get()
        assert source.domain == "juggler.com"
        assert source.leads_found == 6
        assert source.calendar_url == "https://www.juggler.com/tour"  # blank doesn't overwrite
        assert source.last_visited_at is not None


# --- Review (frontend API) ---------------------------------------------------------------


@pytest.mark.django_db
class TestAccept:
    def test_creates_seed_and_copies_it_to_users(
        self, admin_client, user, django_capture_on_commit_callbacks
    ):
        candidate = make_candidate(
            subtype="CIRCUS",
            application_type="FORM",
            application_url="https://foundfest.be/apply",
            approximate_date="mid July",
            relevance_reason="Private reasoning",
            contacts=[{"name": "Ana", "email": "ana@foundfest.be", "role": "Programmer"}],
        )

        with django_capture_on_commit_callbacks(execute=True):
            response = admin_client.post(f"/api/discovery/candidates/{candidate.id}/accept/")

        assert response.status_code == 200
        assert response.data["state"] == "ACCEPTED"
        seed = Festival.objects.get(user__isnull=True, name="Found Fest")
        assert response.data["created_seed"] == {"org_type": "FESTIVAL", "id": seed.id}
        assert seed.is_seed_clone is False
        assert (seed.country, seed.town, seed.website_url) == (
            "Belgium",
            "Ghent",
            "https://foundfest.be",
        )
        assert (seed.festival_type, seed.application_type) == ("CIRCUS", "FORM")
        assert seed.approximate_date == "mid July"
        assert seed.comments == "application: https://foundfest.be/apply"  # cleaned (lowercased)
        assert "Private reasoning" not in seed.comments
        contact = FestivalContact.objects.get(festival=seed)
        assert (contact.name, contact.email, contact.role, contact.user) == (
            "Ana",
            "ana@foundfest.be",
            "Programmer",
            None,
        )
        # Copied to the existing non-staff user through propagate_seed.
        clone = Festival.objects.get(user=user, name="Found Fest")
        assert clone.is_seed_clone is True
        assert clone.contacts.get().email == "ana@foundfest.be"

    def test_overrides_including_type(self, admin_client):
        candidate = make_candidate(application_type="OPEN_CALL")

        response = admin_client.post(
            f"/api/discovery/candidates/{candidate.id}/accept/",
            {"org_type": "RESIDENCY", "name": "Renamed Res", "town": "Bruges"},
            format="json",
        )

        assert response.status_code == 200
        residency = Residency.objects.get(user__isnull=True)
        assert (residency.name, residency.town) == ("Renamed Res", "Bruges")
        assert residency.application_type == "OPEN_CALL"
        assert not Festival.objects.filter(user__isnull=True).exists()

    def test_venue_and_unknown_choices_fall_back_to_defaults(self, admin_client):
        venue_candidate = make_candidate(org_type="VENUE", name="Hall", subtype="THEATRE")
        fest_candidate = make_candidate(
            name="Odd Fest", subtype="NOPE", application_type="NOPE", domain=""
        )

        admin_client.post(f"/api/discovery/candidates/{venue_candidate.id}/accept/")
        admin_client.post(f"/api/discovery/candidates/{fest_candidate.id}/accept/")

        assert Venue.objects.get(user__isnull=True).venue_type == "THEATRE"
        festival = Festival.objects.get(user__isnull=True)
        assert (festival.festival_type, festival.application_type) == ("STREET", "UNKNOWN")

    def test_invalid_override(self, admin_client):
        candidate = make_candidate()

        response = admin_client.post(
            f"/api/discovery/candidates/{candidate.id}/accept/",
            {"org_type": "CIRCUS"},
            format="json",
        )

        assert response.status_code == 400
        assert not Festival.objects.filter(user__isnull=True).exists()

    def test_accepting_twice_creates_one_seed(self, admin_client):
        candidate = make_candidate()

        first = admin_client.post(f"/api/discovery/candidates/{candidate.id}/accept/")
        second = admin_client.post(f"/api/discovery/candidates/{candidate.id}/accept/")

        assert second.status_code == 200
        assert second.data["created_seed"] == first.data["created_seed"]
        assert Festival.objects.filter(user__isnull=True).count() == 1

    @pytest.mark.parametrize("state", ["DISMISSED", "ALREADY_KNOWN"])
    def test_cannot_accept_from_state(self, admin_client, state):
        candidate = make_candidate(state=state)

        response = admin_client.post(f"/api/discovery/candidates/{candidate.id}/accept/")

        assert response.status_code == 400
        assert not Festival.objects.filter(user__isnull=True).exists()

    def test_unresolved_can_be_accepted_with_a_website(self, admin_client):
        candidate = make_candidate(state="UNRESOLVED", website_url="", domain="")

        response = admin_client.post(
            f"/api/discovery/candidates/{candidate.id}/accept/",
            {"website_url": "https://found-it.org"},
            format="json",
        )

        assert response.status_code == 200
        candidate.refresh_from_db()
        assert candidate.domain == "found-it.org"

    def test_credits_the_source_that_led_to_it(self, admin_client):
        DiscoverySource.objects.create(
            url="https://juggler.com/", domain="juggler.com", kind="ARTIST_SITE"
        )
        candidate = make_candidate(
            found_via=[
                {"kind": "SEARCH", "url": "https://search.example/?q=juggler"},
                {"kind": "ARTIST_SITE", "url": "https://www.juggler.com/tour"},
            ]
        )

        admin_client.post(f"/api/discovery/candidates/{candidate.id}/accept/")

        assert DiscoverySource.objects.get().candidates_accepted == 1

    def test_credits_sources_with_lowercase_kinds_from_the_service(self, admin_client):
        DiscoverySource.objects.create(
            url="https://juggler.com/", domain="juggler.com", kind="ARTIST_SITE"
        )
        candidate = make_candidate(
            found_via=[
                {"kind": "artist_site", "url": "https://juggler.com/"},
                {"kind": "calendar", "url": "https://juggler.com/agenda/"},
                {"kind": "festival_site", "url": "https://fest.org/"},
            ]
        )

        admin_client.post(f"/api/discovery/candidates/{candidate.id}/accept/")

        assert DiscoverySource.objects.get().candidates_accepted == 1


@pytest.mark.django_db
class TestDismissRestore:
    def test_dismiss_and_restore(self, admin_client):
        candidate = make_candidate()

        dismissed = admin_client.post(
            f"/api/discovery/candidates/{candidate.id}/dismiss/",
            {"reason": "WRONG_REGION"},
            format="json",
        )
        assert (dismissed.data["state"], dismissed.data["dismiss_reason"]) == (
            "DISMISSED",
            "WRONG_REGION",
        )

        restored = admin_client.post(f"/api/discovery/candidates/{candidate.id}/restore/")
        assert (restored.data["state"], restored.data["dismiss_reason"]) == ("PENDING", "")

    def test_restore_without_website_goes_back_to_unresolved(self, admin_client):
        candidate = make_candidate(state="DISMISSED", website_url="", domain="")

        response = admin_client.post(f"/api/discovery/candidates/{candidate.id}/restore/")

        assert response.data["state"] == "UNRESOLVED"

    def test_dismiss_defaults_reason_and_rejects_bad_reason(self, admin_client):
        first = make_candidate()
        second = make_candidate(name="Second")

        ok = admin_client.post(f"/api/discovery/candidates/{first.id}/dismiss/")
        bad = admin_client.post(
            f"/api/discovery/candidates/{second.id}/dismiss/", {"reason": "BORED"}, format="json"
        )

        assert ok.data["dismiss_reason"] == "OTHER"
        assert bad.status_code == 400

    def test_cannot_dismiss_accepted_or_restore_pending(self, admin_client):
        accepted = make_candidate(state="ACCEPTED")
        pending = make_candidate(name="Pending")

        assert (
            admin_client.post(f"/api/discovery/candidates/{accepted.id}/dismiss/").status_code
            == 400
        )
        assert (
            admin_client.post(f"/api/discovery/candidates/{pending.id}/restore/").status_code == 400
        )

    def test_filter_by_state(self, admin_client):
        make_candidate(name="A")
        make_candidate(name="B", state="DISMISSED")

        response = admin_client.get("/api/discovery/candidates/?state=PENDING")

        assert [c["name"] for c in response.data["results"]] == ["A"]
