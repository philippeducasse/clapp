# Tenant Partitioning Migration Plan

## Overview
Implement schema-based multi-tenancy for PostgreSQL production environment while keeping SQLite for local development. Migrate existing data from public schema into per-user schemas.

## Current State

### What's Already Implemented
1. **Middleware (clapp_backend/middleware.py)** - DONE
   - TenantMiddleware added with production-only check
   - Only activates when `DEBUG=False` AND database engine is PostgreSQL
   - Sets PostgreSQL search_path to `user_{id}` schema on authenticated requests

2. **Signal Handler (profiles/signals.py)** - DONE
   - Post-save signal on Profile model
   - Automatically creates `user_{id}` schema when new user is created
   - Creates tables in user schema based on template schema
   - Copies initial data from template schema

3. **Settings**
   - local.py: DEBUG=True, SQLite by default
   - prod.py: DEBUG=False, PostgreSQL

### What Needs to Be Done
1. Create template schema with reference data
2. Migrate existing data into per-user schemas for existing users
3. Verify the setup works end-to-end

---

## Data Structure Analysis

### Tables to Copy Per-User (Reference Data)
These tables are shared across all users but copied into each user's schema for isolation:
- **venues_venue** - All venue records
- **festivals_festival** - All festival records
- **residencies_residency** - All residency records

Related contacts (also copied):
- **venues_venuecontact** - Contact info for venues
- **festivals_festivalcontact** - Contact info for festivals
- **residencies_residencycontact** - Contact info for residencies

### Tables to Keep in Public Schema
- **applications_application** - User applications to organisations (stays in public)
- **profiles_profile** - User account data (stays in public)
- **performances_performance** - User performances (stays in public, but should be per-user schema - see notes)
- Other user-specific data

### Model Relationships
```
User (Profile)
  ├── Performances (owned by user)
  ├── Applications (user's applications to organisations)
  ├── EmailTemplates (user's custom templates)
  └── Reminders (user's organisation reminders)

Organisations (Shared Reference Data)
  ├── Venues (shared across all users)
  ├── Festivals (shared across all users)
  └── Residencies (shared across all users)
```

---

## Migration Strategy

### Phase 1: Set Up Template Schema
Copy all reference data from current public schema to template schema:

```sql
-- Create template schema
CREATE SCHEMA IF NOT EXISTS template;

-- Copy venues
CREATE TABLE template.venues_venue (LIKE public.venues_venue INCLUDING ALL);
INSERT INTO template.venues_venue SELECT * FROM public.venues_venue;
CREATE TABLE template.venues_venuecontact (LIKE public.venues_venuecontact INCLUDING ALL);
INSERT INTO template.venues_venuecontact SELECT * FROM public.venues_venuecontact;

-- Copy festivals
CREATE TABLE template.festivals_festival (LIKE public.festivals_festival INCLUDING ALL);
INSERT INTO template.festivals_festival SELECT * FROM public.festivals_festival;
CREATE TABLE template.festivals_festivalcontact (LIKE public.festivals_festivalcontact INCLUDING ALL);
INSERT INTO template.festivals_festivalcontact SELECT * FROM public.festivals_festivalcontact;

-- Copy residencies
CREATE TABLE template.residencies_residency (LIKE public.residencies_residency INCLUDING ALL);
INSERT INTO template.residencies_residency SELECT * FROM public.residencies_residency;
CREATE TABLE template.residencies_residencycontact (LIKE public.residencies_residencycontact INCLUDING ALL);
INSERT INTO template.residencies_residencycontact SELECT * FROM public.residencies_residencycontact;
```

### Phase 2: Migrate Existing Users
Create per-user schemas and populate with template data for all existing profiles:

**Option A: Django Management Command** (Recommended)
- Create `clapp_backend/management/commands/migrate_tenant_schemas.py`
- Iterates through all existing Profile objects
- Creates schema for each user
- Populates with template data using the same logic as the signal
- Safe: uses `CREATE SCHEMA IF NOT EXISTS` to avoid errors on re-runs

**Option B: Raw SQL Migration**
- One-off SQL script to create all user schemas
- Less flexible but faster for one-time setup

### Phase 3: Verification
- [ ] Verify template schema has all data
- [ ] Run migration command for existing users
- [ ] Test authentication in production environment
- [ ] Confirm data is accessible in user schema
- [ ] Confirm local SQLite dev environment still works

---

## Implementation Steps

### Step 1: Create Management Command
Location: `clapp_backend/management/commands/migrate_tenant_schemas.py`

```python
from django.core.management.base import BaseCommand
from django.db import connection
from profiles.models import Profile
import logging

class Command(BaseCommand):
    help = "Create tenant schemas for all existing users"

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)

        profiles = Profile.objects.all()
        tables = ["venues_venue", "venues_venuecontact",
                  "festivals_festival", "festivals_festivalcontact",
                  "residencies_residency", "residencies_residencycontact"]

        for profile in profiles:
            schema_name = f"user_{profile.id}"
            quoted_schema = connection.ops.quote_name(schema_name)

            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {quoted_schema}")

                    for table in tables:
                        quoted_table = connection.ops.quote_name(table)
                        cursor.execute(f"""
                            CREATE TABLE IF NOT EXISTS {quoted_schema}.{quoted_table}
                            (LIKE template.{quoted_table} INCLUDING ALL)
                        """)
                        cursor.execute(f"""
                            INSERT INTO {quoted_schema}.{quoted_table}
                            SELECT * FROM template.{quoted_table}
                        """)

                logger.info(f"Schema created for user {profile.id} ({profile.email})")
            except Exception as e:
                logger.error(f"Failed to create schema for user {profile.id}: {e}")
                raise
```

### Step 2: Create Template Schema in Production
- Connect to production PostgreSQL database
- Run the template schema SQL (Phase 1 above)

### Step 3: Run Migration Command
```bash
python manage.py migrate_tenant_schemas
```

### Step 4: Test
- Log in to production as different users
- Verify they can access venues/festivals/residencies
- Verify local SQLite development still works

---

## Key Decisions Made

1. **Production-Only Activation** - Tenant partitioning only active when `DEBUG=False` AND PostgreSQL
2. **Shared Reference Data Model** - Organisations are copied into each user schema as reference data
3. **Auto-Creation via Signal** - New users automatically get their schema via post_save signal
4. **One-Time Migration** - Existing users migrated via management command

---

## Potential Issues & Notes

- **Performance**: Copying all organisations into each user schema duplicates data. Consider indexes on template tables.
- **Sync Issues**: If organisations are updated in public schema, user schemas won't see updates. Consider keeping org tables in public schema and querying across schemas if needed.
- **Contact Cascades**: The soft-delete cascade on organisation contacts may need adjustment for multi-schema setup.

---

## Files Affected

- ✅ `clapp_backend/middleware.py` - Already updated with production check
- 📝 `clapp_backend/management/commands/migrate_tenant_schemas.py` - To be created
- 📋 Production PostgreSQL database - Manual template schema creation
- 📋 `profiles/signals.py` - Already has schema creation signal (no changes needed)
