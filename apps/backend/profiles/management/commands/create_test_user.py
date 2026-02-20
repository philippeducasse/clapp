from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create test users for E2E testing"

    def handle(self, *args, **options):
        self.stdout.write("Running migrations...")
        call_command("migrate", "--noinput")
        test_users = [
            {
                "email": "test@test.com",
                "password": "TestPassword123!",
                "first_name": "Test",
                "last_name": "User",
                "email_host": "GMAIL",
                "email_host_user": "test@test.com",
                "email_host_password": "TestPassword123!",
            },
            {
                "email": "test2@test.com",
                "password": "TestPassword123!",
                "first_name": "Test",
                "last_name": "User2",
                "email_host": "GMAIL",
                "email_host_user": "test@test.com",
                "email_host_password": "TestPassword123!",
            },
        ]

        for user_data in test_users:
            email = user_data.pop("email")
            password = user_data.pop("password")

            if User.objects.filter(email=email).exists():
                self.stdout.write(f"User {email} already exists")
                continue

            User.objects.create_user(email=email, password=password, **user_data)

            self.stdout.write(self.style.SUCCESS(f"✓ Created user: {email}"))
