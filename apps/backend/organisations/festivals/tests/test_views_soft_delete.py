from datetime import date

import pytest
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.test import APIClient

from applications.models import Application
from organisations.festivals.models import Festival, FestivalContact
from profiles.models import Profile


@pytest.mark.django_db
class TestFestivalViewSetSoftDelete:
    """Test soft delete functionality in Festival ViewSet"""

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def user(self):
        return Profile.objects.create_user(email="test@example.com", password="testpass")

    @pytest.fixture
    def authenticated_client(self, client, user):
        client.force_authenticate(user=user)
        return client

    def test_delete_endpoint_soft_deletes(self, authenticated_client):
        """Test that DELETE endpoint performs soft delete"""
        festival = Festival.objects.create(name="Test Festival")
        festival_id = festival.id

        response = authenticated_client.delete(f"/api/festivals/{festival.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Should not appear in default list
        list_response = authenticated_client.get("/api/festivals/")
        # Handle paginated response
        results = (
            list_response.data.get("results", list_response.data)
            if isinstance(list_response.data, dict)
            else list_response.data
        )
        festival_ids = [f["id"] for f in results]
        assert festival_id not in festival_ids

        # Should still exist in database
        deleted_festival = Festival.objects.with_deleted().get(id=festival_id)
        assert deleted_festival.deleted_at is not None

    def test_list_excludes_deleted_by_default(self, authenticated_client):
        """Test that list endpoint excludes deleted festivals by default"""
        f2 = Festival.objects.create(name="Deleted")
        f2.delete()

        response = authenticated_client.get("/api/festivals/")

        assert response.status_code == status.HTTP_200_OK
        # Handle paginated response
        results = (
            response.data.get("results", response.data)
            if isinstance(response.data, dict)
            else response.data
        )
        festival_names = [f["name"] for f in results]
        assert "Active" in festival_names
        assert "Deleted" not in festival_names

    def test_list_includes_deleted_with_parameter(self, authenticated_client):
        """Test that list endpoint includes deleted when include_deleted=true"""
        f2 = Festival.objects.create(name="Deleted")
        f2.delete()

        response = authenticated_client.get("/api/festivals/?include_deleted=true")

        assert response.status_code == status.HTTP_200_OK
        # Handle paginated response
        results = (
            response.data.get("results", response.data)
            if isinstance(response.data, dict)
            else response.data
        )
        festival_names = [f["name"] for f in results]
        assert "Active" in festival_names
        assert "Deleted" in festival_names

    def test_list_includes_deleted_false_excludes_deleted(self, authenticated_client):
        """Test that include_deleted=false still excludes deleted festivals"""
        f2 = Festival.objects.create(name="Deleted")
        f2.delete()

        response = authenticated_client.get("/api/festivals/?include_deleted=false")

        assert response.status_code == status.HTTP_200_OK
        # Handle paginated response
        results = (
            response.data.get("results", response.data)
            if isinstance(response.data, dict)
            else response.data
        )
        festival_names = [f["name"] for f in results]
        assert "Active" in festival_names
        assert "Deleted" not in festival_names

    def test_retrieve_deleted_festival_fails_by_default(self, authenticated_client):
        """Test that retrieving a deleted festival fails without include_deleted"""
        festival = Festival.objects.create(name="Test Festival")
        festival_id = festival.id
        festival.delete()

        response = authenticated_client.get(f"/api/festivals/{festival_id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_restore_endpoint(self, authenticated_client):
        """Test the restore endpoint"""
        festival = Festival.objects.create(name="Test Festival")
        festival_id = festival.id
        festival.delete()

        response = authenticated_client.post(f"/api/festivals/{festival_id}/restore/")

        assert response.status_code == status.HTTP_200_OK
        assert "restored successfully" in response.data["message"]
        assert response.data["data"]["id"] == festival_id
        assert response.data["data"]["deleted_at"] is None

        # Should now appear in default list
        list_response = authenticated_client.get("/api/festivals/")
        # Handle paginated response
        results = (
            list_response.data.get("results", list_response.data)
            if isinstance(list_response.data, dict)
            else list_response.data
        )
        festival_ids = [f["id"] for f in results]
        assert festival_id in festival_ids

    def test_restore_active_festival_returns_error(self, authenticated_client):
        """Test that restoring a non-deleted festival returns error"""
        festival = Festival.objects.create(name="Test Festival")

        response = authenticated_client.post(f"/api/festivals/{festival.id}/restore/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not deleted" in response.data["error"]

    def test_restore_nonexistent_festival_returns_404(self, authenticated_client):
        """Test that restoring a non-existent festival returns 404"""
        response = authenticated_client.post("/api/festivals/99999/restore/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_deleted_at_in_serializer_response(self, authenticated_client):
        """Test that deleted_at field is included in API responses"""
        festival = Festival.objects.create(name="Test Festival")

        # Get active festival
        response = authenticated_client.get(f"/api/festivals/{festival.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert "deleted_at" in response.data
        assert response.data["deleted_at"] is None

        # Soft delete
        festival.delete()

        # Get deleted festival with include_deleted
        response = authenticated_client.get(f"/api/festivals/{festival.id}/?include_deleted=true")
        assert response.status_code == status.HTTP_200_OK
        assert "deleted_at" in response.data
        assert response.data["deleted_at"] is not None

    def test_delete_cascades_shown_in_response(self, authenticated_client):
        """Test that deleting festival with contacts cascades properly"""
        festival = Festival.objects.create(name="Test Festival")
        FestivalContact.objects.create(
            festival=festival, name="Contact 1", email="contact1@example.com"
        )
        FestivalContact.objects.create(
            festival=festival, name="Contact 2", email="contact2@example.com"
        )

        response = authenticated_client.delete(f"/api/festivals/{festival.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify contacts were soft deleted
        assert FestivalContact.objects.count() == 0
        assert FestivalContact.objects.with_deleted().count() == 2

    def test_restore_cascades_to_contacts_via_api(self, authenticated_client):
        """Test that restore endpoint restores contacts"""
        festival = Festival.objects.create(name="Test Festival")
        contact = FestivalContact.objects.create(
            festival=festival, name="Contact", email="contact@example.com"
        )
        contact_id = contact.id

        # Delete via API
        authenticated_client.delete(f"/api/festivals/{festival.id}/")
        assert FestivalContact.objects.filter(id=contact_id).count() == 0

        # Restore via API
        response = authenticated_client.post(f"/api/festivals/{festival.id}/restore/")
        assert response.status_code == status.HTTP_200_OK

        # Contact should be restored
        restored_contact = FestivalContact.objects.get(id=contact_id)
        assert restored_contact.deleted_at is None

    def test_deleted_at_is_read_only(self, authenticated_client):
        """Test that deleted_at cannot be set via API"""
        from django.utils import timezone

        response = authenticated_client.post(
            "/api/festivals/",
            {
                "name": "Test Festival",
                "deleted_at": timezone.now().isoformat(),
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        festival = Festival.objects.get(id=response.data["id"])
        # deleted_at should be None despite being in POST data
        assert festival.deleted_at is None

    def test_applications_filtered_in_deleted_festival(self, authenticated_client, user):
        """Test that deleted festivals don't show deleted applications"""
        festival = Festival.objects.create(name="Test Festival")

        content_type = ContentType.objects.get_for_model(Festival)
        app1 = Application.objects.create(
            content_type=content_type,
            object_id=festival.id,
            profile=user,
            application_date=date(2026, 1, 1),
        )

        # Delete one application
        app1.delete()

        # Get festival - should only show active application
        response = authenticated_client.get(f"/api/festivals/{festival.id}/")
        assert response.status_code == status.HTTP_200_OK

        # has_application_this_year should be True (app2 exists)
        assert response.data["has_application_this_year"] is True

    def test_unauthenticated_cannot_delete(self, client):
        """Test that unauthenticated users cannot delete festivals"""
        festival = Festival.objects.create(name="Test Festival")

        response = client.delete(f"/api/festivals/{festival.id}/")

        # Should require authentication
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

        # Festival should still exist
        assert Festival.objects.filter(id=festival.id).exists()

    def test_unauthenticated_cannot_restore(self, client):
        """Test that unauthenticated users cannot restore festivals"""
        festival = Festival.objects.create(name="Test Festival")
        festival.delete()

        response = client.post(f"/api/festivals/{festival.id}/restore/")

        # Should require authentication
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
