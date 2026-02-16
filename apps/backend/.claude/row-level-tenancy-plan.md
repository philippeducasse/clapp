# Plan: Migrate from Schema-per-User to Row-Level Tenancy

## Context

The current system uses PostgreSQL schema-per-user isolation. Each user gets a `user_N` schema with copies of 6 organisation/contact tables (~800 rows each). This approach doesn't scale - it creates 6 tables per user, makes migrations painful, and was the wrong recommendation for this use case.

The fix: add a `user` FK column to each org model and filter by user in querysets. Seed data (the ~800 orgs) is stored with `user=NULL` and cloned per-user on registration. There is currently ONE user (id=2) with data in a `user_2` schema that needs migrating back.

---

## Step 1: Add `user` FK to abstract models

**File: `organisations/models.py`**

Add to both `Organisation` and `OrganisationContact` abstract models:

```python
user = models.ForeignKey(
    "profiles.Profile",
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name="%(app_label)s_%(class)s_set",
)
```

- `null=True` — rows with `user=NULL` are seed/template data, never shown to users directly
- Since these are abstract models, Django generates migrations in each concrete app (festivals, venues, residencies)

Run `makemigrations` and `migrate`.

---

## Step 2: Data migration — move user_2 schema into public tables

**New migration: `profiles/migrations/0016_migrate_tenant_data.py`**

For each of the 6 tables:
1. Read all rows from `user_2.<table>`
2. Insert into `public.<table>` with `user_id=2`, letting PostgreSQL assign new PKs
3. Build `old_pk -> new_pk` mapping
4. Remap contact FKs (e.g. `festival_id`) using the mapping
5. Update `applications_application.object_id` for `profile_id=2` using the mapping
6. Drop `user_2` and `template` schemas

Skip if not PostgreSQL (local SQLite dev).

---

## Step 3: Update views to filter by user

**`organisations/festivals/views.py`** — add `.filter(user=self.request.user)` to `get_queryset()`
**`organisations/venues/views.py`** — same
**`organisations/residencies/views.py`** — same

**`organisations/views.py`** (base OrganisationViewSet):
- `perform_create()` — pass `user=self.request.user` to `serializer.save()`
- `restore()` — scope lookup by `user=self.request.user`
- `search()` — add `user=request.user` filter to all queries
- `upload()` — stamp `user=request.user` on created orgs and contacts
- `domain_exists()` — scope by `user=request.user`

**`organisations/services.py`** — add `profile` filter to `get_or_create_application` query (pre-existing bug)

---

## Step 4: Update serializers

**`organisations/venues/serializer.py`** — uses `fields = "__all__"` which would expose `user`. Either switch to explicit fields list or add `user` to `read_only_fields`.

**`organisations/serializers.py`** — update `handle_nested_contacts()` to accept and pass `user` when creating contacts.

**`organisations/festivals/serializer.py`** and **`organisations/residencies/serializer.py`** — pass `user=instance.user` to `handle_nested_contacts()`.

Festival and residency serializers already use explicit field lists that don't include `user` — no other changes needed.

---

## Step 5: Replace registration signal

**`profiles/signals.py`** — remove `create_database_schema` and `SchemaCreationError`. Replace with:

```python
@receiver(post_save, sender=Profile, dispatch_uid="seed_user_organisations")
def seed_user_organisations(sender, instance, created, raw, **kwargs):
    if not created or raw:
        return
    # For each org type: bulk clone seed rows (user=NULL) with user=instance
    # For each contact type: bulk clone contacts, remapping org FKs
```

Use `bulk_create` for efficiency (~6 queries total instead of 800+ individual inserts).

---

## Step 6: Remove old tenant infrastructure

- **Delete** `clapp_backend/middleware.py` (TenantMiddleware)
- **Delete** `clapp_backend/db_router.py` (set_tenant_schema, get_tenant_schema, TenantRouter)
- **`conf/settings/base.py`** — remove `"clapp_backend.middleware.TenantMiddleware"` from MIDDLEWARE
- Leave migration `0015_setup_tenant_schemas.py` in place (never delete historical migrations)

---

## Step 7: Update tests

Update test fixtures and test cases to create orgs with `user=profile` and ensure API tests authenticate before requests.

---

## Files to modify

| File | Change |
|------|--------|
| `organisations/models.py` | Add `user` FK to `Organisation` and `OrganisationContact` |
| `organisations/views.py` | `perform_create`, `search`, `upload`, `restore` — scope by user |
| `organisations/serializers.py` | `handle_nested_contacts` — accept/pass `user` |
| `organisations/festivals/views.py` | Filter queryset by user |
| `organisations/festivals/serializer.py` | Pass `user` to `handle_nested_contacts` |
| `organisations/venues/views.py` | Filter queryset by user |
| `organisations/venues/serializer.py` | Exclude `user` from API |
| `organisations/residencies/views.py` | Filter queryset by user |
| `organisations/residencies/serializer.py` | Pass `user` to `handle_nested_contacts` |
| `organisations/services.py` | Fix `get_or_create_application` filter |
| `profiles/signals.py` | Replace schema signal with seed-cloning signal |
| `clapp_backend/middleware.py` | Delete |
| `clapp_backend/db_router.py` | Delete |
| `conf/settings/base.py` | Remove TenantMiddleware from MIDDLEWARE |
| New migration `profiles/0016_...` | Data migration for user_2 |

---

## Verification

1. Run `makemigrations` — should create migrations for user FK in festivals, venues, residencies apps
2. Run `migrate` — adds columns and runs data migration
3. Verify user 2 sees their orgs: `Festival.objects.filter(user_id=2).count()` should match previous count
4. Verify seed data exists: `Festival.objects.filter(user__isnull=True).count()` should be ~800
5. Verify applications still link correctly: check that existing applications resolve their `organisation` GenericFK
6. Create a new test user — verify they get cloned seed data
7. Run full test suite: `uv run pytest`
8. Verify `\dn` in psql no longer shows `user_2` or `template` schemas
