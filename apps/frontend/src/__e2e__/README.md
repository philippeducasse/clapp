# End-to-End (E2E) Tests

These tests run against the actual backend API instead of using mocks. They verify real-world scenarios and integration points.

## Prerequisites

Before running E2E tests:

1. **Backend must be running**
   ```bash
   # Start your backend (typically on http://localhost:8000)
   python manage.py runserver 0.0.0.0:8000
   ```

2. **Test user must exist in database**
   ```bash
   # Create test user via Django shell or admin panel
   Email: test@example.com
   Password: TestPassword123!
   ```

3. **Environment variables configured**
   ```bash
   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   ```

## Running E2E Tests

### Interactive mode (watch)
```bash
npm run test:e2e
```

### Single run
```bash
npm run test:e2e:run
```

### With UI
```bash
npm run test:e2e:ui
```

### Run specific test file
```bash
npm run test:e2e -- auth.e2e.test.ts
```

### Run specific test suite
```bash
npm run test:e2e -- --grep "Authentication"
```

## Test Files

- **auth.e2e.test.ts** - Authentication flows (login, logout, session)
- **festivals.e2e.test.ts** - Festival CRUD, applications, email generation
- **profiles.e2e.test.ts** - Profile updates, performance management

## Test Structure

Each E2E test:

1. **Waits for backend** - Checks backend is ready before running
2. **Authenticates** - Logs in with test credentials
3. **Makes real API calls** - Actual HTTP requests, no mocking
4. **Validates responses** - Checks status codes and data structure
5. **Handles edge cases** - Gracefully skips if test data unavailable

## Customization

### Update Test User

Edit `src/__e2e__/setup.ts`:

```typescript
export const TEST_USER = {
  email: 'your-test@email.com',
  password: 'YourPassword123!',
  firstName: 'Your',
  lastName: 'Name',
};
```

### Change Backend URL

Either:
1. Set environment variable: `NEXT_PUBLIC_BACKEND_URL=http://your-backend:8000`
2. Or modify `src/__e2e__/setup.ts`

### Adjust Timeouts

In `vitest.e2e.config.ts`:

```typescript
testTimeout: 60000, // Increase if API is slow
```

## Database Considerations

E2E tests make real database changes. Consider:

1. **Use test database** - Run against a separate test database
2. **Seed data** - Ensure test data exists (festivals, residencies, etc.)
3. **Cleanup** - Implement cleanup in `src/__e2e__/setup.ts` if needed

## Debugging

### Verbose output
```bash
npm run test:e2e:run -- --reporter=verbose
```

### Debug specific request
Add logging in test:
```typescript
console.log('Response:', await response.json());
```

### Check backend logs
Monitor your backend for errors during test run

## Common Issues

### "Backend not available"
- Ensure backend is running on configured URL
- Check `NEXT_PUBLIC_BACKEND_URL` environment variable

### "Login failed"
- Verify test user exists in database
- Check credentials in `setup.ts`
- Verify CSRF token handling if needed

### "401 Unauthorized"
- Session cookie may not be persisting
- Check backend session configuration
- Verify credentials are correct

### "Application not found"
- Some endpoints may return 404 if feature not implemented
- Tests gracefully skip these cases

## Adding New E2E Tests

1. Create new file in `src/__e2e__/` with `.e2e.test.ts` suffix
2. Import helpers from `setup.ts`
3. Call `waitForBackend()` in `beforeAll()`
4. Use `credentials: 'include'` for authenticated requests
5. Handle cases where test data may not exist

Example:

```typescript
import { describe, it, expect, beforeAll } from 'vitest';
import { waitForBackend, API_BASE, loginTestUser } from './setup';

describe('E2E: My Feature', () => {
  beforeAll(async () => {
    await waitForBackend();
    await loginTestUser();
  });

  it('should fetch data', async () => {
    const response = await fetch(`${API_BASE}/my-endpoint/`, {
      method: 'GET',
      credentials: 'include',
    });

    expect(response.ok).toBe(true);
    const data = await response.json();
    expect(data.id).toBeDefined();
  });
});
```

## Tips

- Tests are slower than unit tests - expect 30s+ runtime
- Use `console.log()` for debugging - visible in output
- Check test database after failures
- Run E2E tests before deployments
- Keep tests independent - don't rely on order
