import pytest
from datetime import date
from applications.models import Application
from organisations.festivals.models import Festival
from profiles.models import Profile
from performances.models import Performance


@pytest.mark.django_db
class TestApplicationModel:
    """Basic tests for the Application model"""

    @pytest.fixture
    def festival(self):
        return Festival.objects.create(name="Test Festival", country="France")

    @pytest.fixture
    def profile(self):
        return Profile.objects.create_user(
            email="test@example.com", password="testpass123"
        )

    @pytest.fixture
    def performance(self, profile):
        return Performance.objects.create(
            performance_title="Test Performance", profile=profile
        )

    def test_application_creation(self, festival, profile):
        """Test creating an application with required fields"""
        application = Application.objects.create(
            organisation=festival,
            profile=profile,
            application_date=date(2025, 3, 15),
            application_status="DRAFT",
        )

        assert application.id is not None
        assert application.organisation == festival
        assert application.profile == profile
        assert application.application_status == "DRAFT"
        assert application.answer_received is False

    def test_application_string_representation(self, festival, profile):
        """Test the __str__ method"""
        application = Application.objects.create(
            organisation=festival, profile=profile, application_date=date(2025, 3, 15)
        )

        assert "Test Festival" in str(application)

    def test_application_year_property(self, festival, profile):
        """Test application_year property calculation"""
        # Test for date before September (returns same year)
        app1 = Application.objects.create(
            organisation=festival, profile=profile, application_date=date(2025, 3, 15)
        )
        assert app1.application_year == 2025

        # Test for date in/after September (returns next year)
        app2 = Application.objects.create(
            organisation=festival, profile=profile, application_date=date(2025, 10, 15)
        )
        assert app2.application_year == 2026

    def test_application_with_performances(self, festival, profile, performance):
        """Test application with performances many-to-many relationship"""
        application = Application.objects.create(
            organisation=festival, profile=profile, application_date=date(2025, 3, 15)
        )
        application.performances.add(performance)

        assert application.performances.count() == 1
        assert performance in application.performances.all()

    def test_application_status_choices(self, festival, profile):
        """Test valid application status choices"""
        statuses = ["DRAFT", "APPLIED", "IN_DISCUSSION", "REJECTED", "ACCEPTED"]

        for status in statuses:
            app = Application.objects.create(
                organisation=festival, profile=profile, application_status=status
            )
            assert app.application_status == status

    def test_application_optional_fields(self, festival, profile):
        """Test that optional fields can be null"""
        application = Application.objects.create(organisation=festival, profile=profile)

        assert application.email_subject is None
        assert application.message is None
        assert application.answer_date is None
        assert application.payment_amount is None
