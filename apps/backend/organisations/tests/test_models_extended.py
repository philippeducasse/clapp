"""Extended tests for organisations/models.py soft delete functionality."""
import pytest
from django.utils import timezone

from organisations.festivals.models import Festival, FestivalContact
from organisations.models import SoftDeleteQuerySet
from profiles.models import Profile


@pytest.mark.django_db
class TestSoftDeleteQuerySet:
    def test_queryset_delete_soft_deletes(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        Festival.objects.create(name="Fest A", town="Paris", country="FR", user=profile)
        Festival.objects.create(name="Fest B", town="Paris", country="FR", user=profile)

        Festival.objects.filter(user=profile).delete()

        alive = Festival.objects.filter(user=profile).count()
        assert alive == 0

        # with_deleted should still show them
        total = Festival.objects.with_deleted().filter(user=profile).count()
        assert total == 2

    def test_queryset_hard_delete_removes(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        Festival.objects.create(name="Fest A", town="Paris", country="FR", user=profile)

        Festival.objects.with_deleted().filter(user=profile).hard_delete()

        total = Festival.objects.with_deleted().filter(user=profile).count()
        assert total == 0

    def test_alive_filter(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        f1 = Festival.objects.create(name="Active Fest", town="Paris", country="FR", user=profile)
        f2 = Festival.objects.create(name="Dead Fest", town="Paris", country="FR", user=profile)
        f2.delete()

        alive = Festival.objects.with_deleted().filter(user=profile).alive()
        assert alive.count() == 1
        assert alive.first().id == f1.id

    def test_deleted_filter(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        Festival.objects.create(name="Active Fest", town="Paris", country="FR", user=profile)
        f2 = Festival.objects.create(name="Dead Fest", town="Paris", country="FR", user=profile)
        f2.delete()

        deleted = Festival.objects.deleted().filter(user=profile)
        assert deleted.count() == 1
        assert deleted.first().id == f2.id

    def test_with_deleted_returns_all(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        f1 = Festival.objects.create(name="Active Fest", town="Paris", country="FR", user=profile)
        f2 = Festival.objects.create(name="Dead Fest", town="Paris", country="FR", user=profile)
        f2.delete()

        all_fests = Festival.objects.with_deleted().filter(user=profile)
        assert all_fests.count() == 2


@pytest.mark.django_db
class TestOrganisationSoftDelete:
    def test_soft_delete_cascades_to_contacts(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Cascade Fest", town="Paris", country="FR", user=profile
        )
        FestivalContact.objects.create(
            festival=festival, email="contact@fest.com", user=profile
        )

        festival.delete()

        # Contact should be soft deleted
        contacts = FestivalContact.objects.with_deleted().filter(festival=festival)
        assert contacts.filter(deleted_at__isnull=False).count() == 1

    def test_restore_cascades_to_contacts(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Restore Fest", town="Paris", country="FR", user=profile
        )
        FestivalContact.objects.create(
            festival=festival, email="contact@fest.com", user=profile
        )

        festival.delete()
        festival.restore()

        # Contact should be restored
        contacts = FestivalContact.objects.filter(festival=festival)
        assert contacts.count() == 1

    def test_hard_delete(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Hard Fest", town="Paris", country="FR", user=profile
        )
        festival_id = festival.id

        festival.hard_delete()

        assert not Festival.objects.with_deleted().filter(id=festival_id).exists()

    def test_soft_delete_applications(self):
        """_soft_delete_applications method."""
        from applications.models import Application
        from django.contrib.contenttypes.models import ContentType

        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="App Fest", town="Paris", country="FR", user=profile
        )
        ct = ContentType.objects.get_for_model(Festival)
        app = Application.objects.create(
            content_type=ct,
            object_id=festival.id,
            profile=profile,
            status="APPLIED",
            application_date=timezone.now().date(),
        )

        festival._soft_delete_applications()

        # Application should be soft deleted
        from applications.models import Application as App
        updated = App.objects.with_deleted().get(id=app.id)
        assert updated.deleted_at is not None

    def test_restore_applications(self):
        """_restore_applications method."""
        from applications.models import Application
        from django.contrib.contenttypes.models import ContentType

        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="App Fest", town="Paris", country="FR", user=profile
        )
        ct = ContentType.objects.get_for_model(Festival)
        app = Application.objects.create(
            content_type=ct,
            object_id=festival.id,
            profile=profile,
            status="APPLIED",
            application_date=timezone.now().date(),
            deleted_at=timezone.now(),
        )

        festival._restore_applications()

        updated = Application.objects.with_deleted().get(id=app.id)
        assert updated.deleted_at is None


@pytest.mark.django_db
class TestOrganisationContactSoftDelete:
    def test_contact_soft_delete(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Contact Fest", town="Paris", country="FR", user=profile
        )
        contact = FestivalContact.objects.create(
            festival=festival, email="info@fest.com", user=profile
        )

        contact.delete()

        assert FestivalContact.objects.filter(id=contact.id).count() == 0
        assert FestivalContact.objects.with_deleted().filter(id=contact.id).count() == 1

    def test_contact_hard_delete(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Contact Fest", town="Paris", country="FR", user=profile
        )
        contact = FestivalContact.objects.create(
            festival=festival, email="info@fest.com", user=profile
        )
        contact_id = contact.id

        contact.hard_delete()

        assert not FestivalContact.objects.with_deleted().filter(id=contact_id).exists()

    def test_contact_restore(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Contact Fest", town="Paris", country="FR", user=profile
        )
        contact = FestivalContact.objects.create(
            festival=festival, email="info@fest.com", user=profile
        )

        contact.delete()
        contact.restore()

        assert FestivalContact.objects.filter(id=contact.id).count() == 1
        assert contact.deleted_at is None
