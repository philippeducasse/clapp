import pytest
from datetime import date
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from organisations.festivals.models import Festival, FestivalContact
from applications.models import Application
from profiles.models import Profile


@pytest.mark.django_db
class TestFestivalSoftDelete:
    """Test soft delete functionality for Festival model"""

    def test_soft_delete_sets_deleted_at(self):
        """Test that deleting a festival sets deleted_at timestamp"""
        festival = Festival.objects.create(name="Test Festival", country="France")
        festival_id = festival.id

        festival.delete()

        # Should not appear in default queryset
        assert Festival.objects.filter(id=festival_id).count() == 0

        # CRITICAL: Verify record still exists in database with with_deleted()
        assert Festival.objects.with_deleted().filter(id=festival_id).count() == 1

        # Should appear in with_deleted queryset with deleted_at set
        deleted_festival = Festival.objects.with_deleted().get(id=festival_id)
        assert deleted_festival.deleted_at is not None
        assert isinstance(deleted_festival.deleted_at, timezone.datetime)

        # Verify other fields are unchanged (not actually deleted)
        assert deleted_festival.name == "Test Festival"
        assert deleted_festival.country == "France"

    def test_cascade_soft_delete_to_contacts(self):
        """Test that soft deleting a festival cascades to contacts"""
        festival = Festival.objects.create(name="Test Festival")
        contact1 = FestivalContact.objects.create(
            festival=festival, name="Contact 1", email="contact1@example.com"
        )
        contact2 = FestivalContact.objects.create(
            festival=festival, name="Contact 2", email="contact2@example.com"
        )
        contact1_id = contact1.id
        contact2_id = contact2.id

        festival.delete()

        # Contacts should be soft deleted (not in default queryset)
        assert FestivalContact.objects.filter(id=contact1_id).count() == 0
        assert FestivalContact.objects.filter(id=contact2_id).count() == 0

        # CRITICAL: Verify contacts still exist in database
        assert FestivalContact.objects.with_deleted().filter(id=contact1_id).count() == 1
        assert FestivalContact.objects.with_deleted().filter(id=contact2_id).count() == 1

        # Contacts should exist in with_deleted queryset with data intact
        deleted_contact1 = FestivalContact.objects.with_deleted().get(id=contact1_id)
        deleted_contact2 = FestivalContact.objects.with_deleted().get(id=contact2_id)
        assert deleted_contact1.deleted_at is not None
        assert deleted_contact2.deleted_at is not None
        # Verify data is preserved
        assert deleted_contact1.name == "Contact 1"
        assert deleted_contact1.email == "contact1@example.com"
        assert deleted_contact2.name == "Contact 2"

    def test_cascade_soft_delete_to_applications(self):
        """Test that soft deleting a festival cascades to applications"""
        festival = Festival.objects.create(name="Test Festival")
        profile = Profile.objects.create_user(email="test@example.com", password="testpass")

        content_type = ContentType.objects.get_for_model(Festival)
        application = Application.objects.create(
            content_type=content_type,
            object_id=festival.id,
            profile=profile,
            application_date=date.today(),
        )
        application_id = application.id

        festival.delete()

        # Application should be soft deleted (not in default queryset)
        assert Application.objects.filter(id=application_id).count() == 0

        # CRITICAL: Verify application still exists in database
        assert Application.objects.with_deleted().filter(id=application_id).count() == 1

        deleted_app = Application.objects.with_deleted().get(id=application_id)
        assert deleted_app.deleted_at is not None
        # Verify relationship data is preserved
        assert deleted_app.object_id == festival.id
        assert deleted_app.profile == profile

    def test_restore_festival(self):
        """Test restoring a soft-deleted festival"""
        festival = Festival.objects.create(name="Test Festival")
        festival_id = festival.id

        festival.delete()
        assert Festival.objects.filter(id=festival_id).count() == 0

        # Restore
        deleted_festival = Festival.objects.with_deleted().get(id=festival_id)
        deleted_festival.restore()

        # Should now appear in default queryset
        restored_festival = Festival.objects.get(id=festival_id)
        assert restored_festival.deleted_at is None

    def test_restore_cascades_to_contacts(self):
        """Test that restoring a festival restores its contacts"""
        festival = Festival.objects.create(name="Test Festival")
        contact = FestivalContact.objects.create(
            festival=festival, name="Test Contact", email="test@example.com"
        )
        contact_id = contact.id

        festival.delete()
        assert FestivalContact.objects.filter(id=contact_id).count() == 0

        # Restore festival
        deleted_festival = Festival.objects.with_deleted().get(id=festival.id)
        deleted_festival.restore()

        # Contact should be restored
        restored_contact = FestivalContact.objects.get(id=contact_id)
        assert restored_contact.deleted_at is None

    def test_restore_cascades_to_applications(self):
        """Test that restoring a festival restores its applications"""
        festival = Festival.objects.create(name="Test Festival")
        profile = Profile.objects.create_user(email="test@example.com", password="testpass")

        content_type = ContentType.objects.get_for_model(Festival)
        application = Application.objects.create(
            content_type=content_type,
            object_id=festival.id,
            profile=profile,
            application_date=date.today(),
        )
        application_id = application.id

        festival.delete()

        # Verify application was deleted
        assert Application.objects.filter(id=application_id).count() == 0

        # Restore festival
        deleted_festival = Festival.objects.with_deleted().get(id=festival.id)
        deleted_festival.restore()

        # Application should be restored
        restored_app = Application.objects.with_deleted().get(id=application_id)
        assert restored_app.deleted_at is None
        # Should also appear in default queryset
        assert Application.objects.filter(id=application_id).exists()

    def test_hard_delete_festival(self):
        """Test that hard delete actually removes from database"""
        festival = Festival.objects.create(name="Test Festival")
        festival_id = festival.id

        festival.hard_delete()

        # CRITICAL: Verify record is ACTUALLY deleted from database
        assert Festival.objects.with_deleted().filter(id=festival_id).count() == 0

        # Double-check using raw query that it's gone from DB
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM festivals_festival WHERE id = %s", [festival_id])
            count = cursor.fetchone()[0]
            assert count == 0, "Record should be completely removed from database"

    def test_queryset_alive_method(self):
        """Test custom queryset alive() method"""
        f1 = Festival.objects.create(name="Active 1")
        f2 = Festival.objects.create(name="Active 2")
        f3 = Festival.objects.create(name="Deleted")
        f3.delete()

        # Test alive() method
        alive_festivals = Festival.objects.alive()
        assert alive_festivals.count() == 2
        assert f1 in alive_festivals
        assert f2 in alive_festivals
        assert f3 not in list(alive_festivals)

    def test_queryset_deleted_method(self):
        """Test custom queryset deleted() method"""
        f1 = Festival.objects.create(name="Active")
        f2 = Festival.objects.create(name="Deleted 1")
        f3 = Festival.objects.create(name="Deleted 2")
        f2.delete()
        f3.delete()

        # Test deleted() method
        deleted_festivals = Festival.objects.deleted()
        assert deleted_festivals.count() == 2
        assert f1 not in list(deleted_festivals)
        assert f2 in deleted_festivals
        assert f3 in deleted_festivals

    def test_queryset_with_deleted_method(self):
        """Test custom queryset with_deleted() method"""
        f1 = Festival.objects.create(name="Active")
        f2 = Festival.objects.create(name="Deleted")
        f2.delete()

        # Test with_deleted() method
        all_festivals = Festival.objects.with_deleted()
        assert all_festivals.count() == 2
        assert f1 in all_festivals
        assert f2 in all_festivals

    def test_default_queryset_excludes_deleted(self):
        """Test that default queryset excludes deleted festivals"""
        f1 = Festival.objects.create(name="Active")
        f2 = Festival.objects.create(name="Deleted")
        f2.delete()

        # Default queryset should only return active
        assert Festival.objects.count() == 1
        assert Festival.objects.first() == f1

    def test_queryset_bulk_delete(self):
        """Test bulk delete on queryset"""
        f1 = Festival.objects.create(name="Festival 1")
        f2 = Festival.objects.create(name="Festival 2")
        f3 = Festival.objects.create(name="Festival 3")
        f1_id = f1.id
        f2_id = f2.id
        f3_id = f3.id

        # Bulk delete
        Festival.objects.filter(name__in=["Festival 1", "Festival 2"]).delete()

        # Should soft delete the filtered festivals (not in default queryset)
        assert Festival.objects.count() == 1

        # CRITICAL: Verify all 3 still exist in database
        assert Festival.objects.with_deleted().count() == 3
        assert Festival.objects.with_deleted().filter(id=f1_id).exists()
        assert Festival.objects.with_deleted().filter(id=f2_id).exists()
        assert Festival.objects.with_deleted().filter(id=f3_id).exists()

        # Verify deleted status
        deleted = Festival.objects.deleted()
        assert deleted.count() == 2
        assert f1 in deleted
        assert f2 in deleted

        # Verify active record
        active = Festival.objects.get(id=f3_id)
        assert active.name == "Festival 3"
        assert active.deleted_at is None

    def test_delete_return_value(self):
        """Test that delete returns correct tuple format"""
        festival = Festival.objects.create(name="Test Festival")

        result = festival.delete()

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == 1  # Total count
        assert isinstance(result[1], dict)  # Model counts
        assert "festivals.Festival" in result[1]
        assert result[1]["festivals.Festival"] == 1

    def test_soft_delete_does_not_delete_unrelated_contacts(self):
        """Test that soft deleting one festival doesn't affect other festivals' contacts"""
        festival1 = Festival.objects.create(name="Festival 1")
        festival2 = Festival.objects.create(name="Festival 2")

        contact1 = FestivalContact.objects.create(
            festival=festival1, name="Contact 1", email="contact1@example.com"
        )
        contact2 = FestivalContact.objects.create(
            festival=festival2, name="Contact 2", email="contact2@example.com"
        )
        contact2_id = contact2.id

        festival1.delete()

        # Festival 1's contact should be deleted
        assert FestivalContact.objects.filter(id=contact1.id).count() == 0

        # Festival 2's contact should still be active
        assert FestivalContact.objects.filter(id=contact2_id).exists()
        active_contact = FestivalContact.objects.get(id=contact2_id)
        assert active_contact.deleted_at is None
