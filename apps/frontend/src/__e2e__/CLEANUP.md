# Test Data Cleanup Strategy

E2E tests now automatically clean up created data after running, keeping your database clean.

## How It Works

### Automatic Tracking
When tests create entities (performances, applications, etc.), they're automatically tracked:

```typescript
const response = await fetchWithAuth(`${API_BASE}/performances/`, {
  method: 'POST',
  body: JSON.stringify(performanceData),
});

if (response.ok) {
  const created = await response.json();
  trackEntity('performance', created.id);  // ← Tracked for cleanup
}
```

### Automatic Cleanup
After each test file runs, `afterAll()` hook cleans up all tracked entities:

```typescript
afterAll(async () => {
  await cleanupTestData();
});
```

### Cleanup Process
1. **Reverse Order (LIFO)** - Last created, first deleted
2. **Type-Specific Endpoints** - Uses correct API endpoint per entity type
3. **Logging** - Shows what's being deleted
4. **Silent Failures** - If deletion fails, continues with others

Example output:
```
🧹 Cleaning up 3 test entities...
  ✓ Deleted performance #42
  ✓ Deleted performance #41
  ✓ Deleted application #10
✓ Cleanup complete
```

## Supported Entity Types

Currently tracks and cleans up:
- `performance` - `/api/performances/{id}`
- `application` - `/api/applications/{id}`
- `festival` - `/api/festivals/{id}`

To add more types, edit `cleanupTestData()` in `setup.ts`:

```typescript
case "venue":
  endpoint = "/venues/";
  break;
```

## Manual Cleanup

If tests are interrupted and data remains:

### Django Shell
```bash
python manage.py shell
>>> from your_app.models import Performance
>>> from django.contrib.auth.models import User
>>> test_user = User.objects.get(email='test@test.com')
>>> Performance.objects.filter(profile=test_user).delete()
```

### SQL
```sql
-- Delete all test performances
DELETE FROM performances WHERE profile_id = (
  SELECT id FROM users WHERE email = 'test@test.com'
);

-- Delete all test applications
DELETE FROM applications WHERE profile_id = (
  SELECT id FROM users WHERE email = 'test@test.com'
);
```

### Using E2E Tests
```typescript
import { cleanupTestData, loginTestUser } from './setup';

// Manually trigger cleanup
await loginTestUser();
await cleanupTestData();
```

## Disabling Cleanup

To keep test data for inspection:

```typescript
// In test file, comment out afterAll:
// afterAll(async () => {
//   await cleanupTestData();
// });
```

Or skip specific tests:
```typescript
it.skip('should create performance', async () => {
  // Won't run, won't create data
});
```

## Troubleshooting

### Data Not Being Deleted
**Cause:** `trackEntity()` not called when entity created
**Solution:** Add `trackEntity()` call after successful creation

```typescript
const created = await response.json();
trackEntity('performance', created.id);  // ✅ Add this
```

### "Failed to delete" Warnings
**Cause:** Entity may already be deleted or permission issue
**Solution:** This is non-fatal, cleanup continues with others

### Database Still Has Test Data
**Options:**
1. Manually run cleanup script
2. Delete test user and cascade delete their data
3. Reset database: `python manage.py flush`

## Best Practices

✅ **Do:**
- Call `trackEntity()` for all created data
- Use `afterAll()` in each test file
- Let cleanup run automatically
- Check logs for cleanup confirmation

❌ **Don't:**
- Assume data is deleted without seeing cleanup logs
- Create data without tracking it
- Interrupt tests during cleanup phase
- Share test user between test files

## Advanced: Custom Cleanup

Add custom cleanup for complex scenarios:

```typescript
export const cleanupTestData = async () => {
  // ... default cleanup ...

  // Custom cleanup
  try {
    // Delete associated files
    await fetch(`${API_BASE}/cleanup/files`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrfToken },
    });
  } catch (error) {
    console.warn('Custom cleanup failed:', error);
  }
};
```

## Cleanup Performance

Cleanup runs sequentially for reliability. For large datasets:
- Single deletion: ~50-100ms
- 10 entities: ~1 second
- 50 entities: ~5 seconds

To speed up:
```typescript
// Parallel deletion (less safe)
await Promise.all(createdEntities.map(entity =>
  deleteEntity(endpoint, entity.id)
));
```

## CI/CD Integration

In GitHub Actions, add cleanup step:

```yaml
- name: Cleanup test data
  if: always()  # Run even if tests fail
  run: npm run test:e2e:cleanup
```

## Monitoring Cleanup

Check cleanup logs in test output:

```bash
npm run test:e2e:run -- --reporter=verbose
# Look for "🧹 Cleaning up" messages
```

Or add debugging:

```typescript
// In setup.ts
console.log('Total entities to cleanup:', createdEntities.length);
createdEntities.forEach(e => console.log(`  - ${e.type} #${e.id}`));
```
