# Backend Setup for E2E Tests

Before running E2E tests, your backend must be properly configured with test data.

## Quick Start

### 1. Start Backend
```bash
cd /path/to/backend
python manage.py runserver 0.0.0.0:8000
```

### 2. Create Test User

Open Django shell:
```bash
python manage.py shell
```

Then run:
```python
from django.contrib.auth.models import User
from your_profile_model import Profile

# Create Django user
user = User.objects.create_user(
    username='test@example.com',
    email='test@example.com',
    password='TestPassword123!'
)

# Create profile
profile = Profile.objects.create(
    user=user,
    email='test@example.com',
    firstName='Test',
    lastName='User'
)

print(f"Created test user: {profile.email}")
```

### 3. Run E2E Tests
```bash
npm run test:e2e:run
```

## Detailed Setup

### Using Management Command (Preferred)

Create `your_app/management/commands/create_test_data.py`:

```python
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from your_profile_model import Profile

class Command(BaseCommand):
    help = 'Create test data for E2E tests'

    def handle(self, *args, **options):
        # Create test user
        user, created = User.objects.get_or_create(
            username='test@example.com',
            defaults={
                'email': 'test@example.com',
                'password': 'TestPassword123!'
            }
        )

        if not created:
            user.set_password('TestPassword123!')
            user.save()

        # Create profile
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'email': 'test@example.com',
                'firstName': 'Test',
                'lastName': 'User'
            }
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Test user ready: {profile.email}'
            )
        )
```

Then run:
```bash
python manage.py create_test_data
```

### Using Django Admin

1. Go to http://localhost:8000/admin
2. Create superuser if needed: `python manage.py createsuperuser`
3. Create user with email: `test@example.com`
4. Create profile with:
   - Email: test@example.com
   - First Name: Test
   - Last Name: User

## Test Data Requirements

For E2E tests to run fully, you should have:

### Basic Data
- ✅ Test user account (test@example.com)
- ✅ Test user profile

### Optional Data (for comprehensive tests)
- At least 1-2 Festivals
- At least 1-2 Venues
- At least 1-2 Residencies
- Sample Performances

If this data doesn't exist, tests gracefully skip those scenarios.

## Environment Setup

Create `.env.local`:
```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

Or export:
```bash
export NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## Verify Backend is Ready

Check if backend is accepting connections:
```bash
curl -s http://localhost:8000/api/profiles/csrf/ | jq .
```

Expected response (with CSRF token):
```json
{
  "csrf_token": "..."
}
```

## Database State

### Fresh Database
```bash
python manage.py migrate
python manage.py create_test_data
```

### Clean Between Test Runs
```bash
# Keep test user, delete test data
python manage.py shell
>>> from your_app.models import Performance, Application
>>> Performance.objects.filter(profile__email='test@example.com').delete()
>>> Application.objects.filter(profile__email='test@example.com').delete()
```

### Complete Reset
```bash
python manage.py flush  # WARNING: Deletes all data
python manage.py migrate
python manage.py create_test_data
```

## Troubleshooting

### "Backend not available"
```bash
# Check if backend is running
lsof -i :8000

# Start backend
python manage.py runserver 0.0.0.0:8000
```

### "Login failed: Unauthorized"
```bash
# Verify test user exists
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.filter(username='test@example.com').exists()
True

# Reset password
>>> user = User.objects.get(username='test@example.com')
>>> user.set_password('TestPassword123!')
>>> user.save()
```

### "403 Forbidden"
- User must be authenticated
- Check session handling in backend
- Verify CSRF token is being sent
- Check backend permissions/groups

### "400 Bad Request"
- Invalid request format
- Missing required fields
- Check backend validation logs

## Database Fixtures

Create fixture for automated setup:

```bash
# Export test data
python manage.py dumpdata --indent 2 \
  auth.user \
  your_app.profile \
  > src/__e2e__/fixtures/test_data.json
```

Load in test setup:
```bash
python manage.py loaddata src/__e2e__/fixtures/test_data.json
```

## CI/CD Integration

For automated testing:

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_PASSWORD: password

    steps:
      - uses: actions/checkout@v2

      - name: Start backend
        run: |
          python manage.py migrate
          python manage.py create_test_data
          python manage.py runserver &

      - name: Wait for backend
        run: sleep 3

      - name: Run E2E tests
        run: npm run test:e2e:run
```

## Cleanup

Tests should be idempotent. However, you can cleanup:

```bash
python manage.py shell
>>> from your_app.models import Application
>>> Application.objects.filter(
...     profile__email='test@example.com',
...     email_subject__icontains='E2E'
... ).delete()
```

## API Endpoint Verification

Test individual endpoints:

```bash
# Get CSRF token
curl -s http://localhost:8000/api/profiles/csrf/

# Login
curl -X POST http://localhost:8000/api/profiles/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPassword123!"}'

# Get profile (with session cookie)
curl -s http://localhost:8000/api/profiles/me/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID"
```
