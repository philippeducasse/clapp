from django.core.management.base import BaseCommand
from profiles.models import Profile


class Command(BaseCommand):
    help = "Create test users for E2E testing"

    def handle(self, *args, **options):
        test_users = [
            {
                "email": "test@test.com",
                "password": "TestPassword123!",
                "first_name": "Test",
                "last_name": "User",
            },
            {
                "email": "test2@test.com",
                "password": "TestPassword123!",
                "first_name": "Test",
                "last_name": "User2",
            },
        ]

        for user_data in test_users:
            email = user_data["email"]
            password = user_data["password"]

            if Profile.objects.filter(email=email).exists():
                self.stdout.write(f"User {email} already exists")
                continue

            Profile.objects.create_user(
                email=email,
                password=password,
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
            )
            self.stdout.write(self.style.SUCCESS(f"✓ Created user: {email}"))
