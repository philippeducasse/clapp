# Data Serialization in E2E Tests

The E2E tests automatically handle camelCase ↔ snake_case conversion, matching your frontend architecture.

## How It Works

The `fetchWithAuth()` helper in `setup.ts` automatically:

### Outgoing (Frontend → Backend)
- Converts camelCase field names to snake_case
- Works for JSON request bodies
- Transparent to test code

Example:
```typescript
// Test code (camelCase)
await fetchWithAuth(`${API_BASE}/profiles/${id}/`, {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    firstName: 'UpdatedName',
    instagramProfile: '@user',
  })
});

// Sent to backend as (snake_case)
{
  "first_name": "UpdatedName",
  "instagram_profile": "@user"
}
```

### Incoming (Backend → Frontend)
- Converts snake_case response fields to camelCase
- Automatically applied to all JSON responses
- Response `.json()` call returns camelCase data

Example:
```typescript
const response = await fetchWithAuth(`${API_BASE}/profiles/me/`);
const profile = await response.json();

// Backend returns:
// { "first_name": "Test", "instagram_profile": "@testuser" }

// Test receives:
// { "firstName": "Test", "instagramProfile": "@testuser" }
```

## Why This Matters

Your backend uses snake_case (Django convention), your frontend uses camelCase (JavaScript convention). The serializer bridges this gap automatically.

### Benefits
✅ Tests use camelCase like the frontend
✅ No manual conversion needed
✅ Matches fetchHelper.ts behavior from client code
✅ Single source of truth for serialization logic

### Limitations
- Only works for JSON bodies
- FormData and multipart uploads are not converted
- Field names must exactly match (case-insensitive)

## Manual Conversion

If you need to manually convert:

```typescript
import {
  transformKeysToCamelCase,
  transformKeysToSnakeCase
} from '@/helpers/serializer';

// Frontend → Backend
const snakeCaseData = transformKeysToSnakeCase(camelCaseData);

// Backend → Frontend
const camelCaseData = transformKeysToCamelCase(snakeCaseData);
```

## Troubleshooting

### Fields are undefined after response
**Cause:** Field names don't match after case conversion
**Solution:** Check field names match your backend model

```typescript
// ✅ Works
firstName → first_name

// ❌ Doesn't work
fullName → full_name (backend uses firstName)
```

### Serialization not applied
**Cause:** Not using `fetchWithAuth()`
**Solution:** Always use `fetchWithAuth()` instead of `fetch()`

```typescript
// ❌ Won't serialize
const response = await fetch(`${API_BASE}/...`);

// ✅ Will serialize
const response = await fetchWithAuth(`${API_BASE}/...`);
```

### FormData not converted
**Cause:** FormData fields don't support automatic conversion
**Solution:** Manually convert FormData fields if needed

```typescript
const formData = new FormData();
formData.append('performance_title', 'My Performance');  // Use snake_case
```

## Testing Serialization

Add logging to verify:

```typescript
// In setup.ts fetchWithAuth, add:
console.log('Sending:', body);

// Then in tests, check console output
const response = await fetchWithAuth(...);
```

## Future Improvements

- [ ] Add FormData serialization support
- [ ] Automatic snake_case field mapping for complex types
- [ ] Validation that backend fields match frontend types
- [ ] Performance optimization for large responses
