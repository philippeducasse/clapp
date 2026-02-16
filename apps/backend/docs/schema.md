# Schema Partitioning - Line by Line Explanation

This system gives each user their own isolated copy of organisation data (venues, festivals, residencies) using PostgreSQL schemas. Users start with a shared pool of public data, but any changes they make only affect their own schema.

There are four files involved:

1. `profiles/migrations/0015_setup_tenant_schemas.py` - one-time migration that creates the template schema
2. `profiles/signals.py` - creates a user schema when a new profile is created
3. `clapp_backend/middleware.py` - routes each request to the correct user schema
4. `clapp_backend/db_router.py` - thread-local storage for the current schema name

---

## 1. Migration: `profiles/migrations/0015_setup_tenant_schemas.py`

This migration runs once during `manage.py migrate`. It creates a `template` schema that holds empty copies of the tenant tables. The template is used as a structural blueprint when creating new user schemas.

```python
def create_schemas(apps, schema_editor):
```
- Called by Django's migration framework. `apps` gives access to models, `schema_editor` gives access to the database connection.

```python
    if schema_editor.connection.vendor != "postgresql":
        return
```
- Guard clause: schema partitioning only works on PostgreSQL. If running on SQLite (e.g. local dev), skip entirely.

```python
    tables = [
        "venues_venue",
        "venues_venuecontact",
        "festivals_festival",
        "festivals_festivalcontact",
        "residencies_residency",
        "residencies_residencycontact",
    ]
```
- The list of tables that get partitioned per-user. These are the Django table names (appname_modelname). Only organisation-related tables are listed here. Tables **not** in this list (like `applications_application`, `auth_user`, `profiles_profile`) never get copied into user schemas - they only exist in `public`. When the middleware sets `search_path TO "user_5", public`, PostgreSQL can't find an `applications` table in `user_5`, so it falls through to `public`. That's why applications are naturally per-user without needing schema isolation - they live in `public` and are filtered by Django's normal queryset logic (e.g. `Application.objects.filter(user=request.user)`).

```python
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("CREATE SCHEMA IF NOT EXISTS template")
```
- Opens a raw SQL cursor and creates a PostgreSQL schema called `template`. Think of a schema as a namespace/folder for tables. `IF NOT EXISTS` makes this safe to run multiple times.

```python
        for table in tables:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS template.{table}
                (LIKE public.{table} INCLUDING ALL)
            """)
```
- For each table, creates a **structurally identical** copy in the `template` schema. `LIKE public.{table} INCLUDING ALL` is a PostgreSQL command that copies only the **table structure** (columns, indexes, constraints, defaults) - it never copies rows. The `template` tables are empty by design. They exist purely as a structural blueprint so we have a clean table definition to clone from when creating user schemas. The actual data seeding happens later in the signal (see below), which copies rows from `public`.

```python
    operations = [
        migrations.RunPython(create_schemas, reverse_code=migrations.RunPython.noop),
    ]
```
- Registers `create_schemas` as a migration operation. `reverse_code=noop` means there is no reverse migration (the template schema won't be dropped on rollback).

```python
    dependencies = [
        ("profiles", "0014_profile_date_format_profile_table_size"),
        ("venues", "0006_venue_deleted_at_venuecontact_deleted_at"),
        ("festivals", "0014_festival_deleted_at_festivalcontact_deleted_at"),
        ("residencies", "0006_residency_deleted_at_residencycontact_deleted_at"),
    ]
```
- Ensures this migration runs after all the relevant tables exist in `public`. Without these dependencies, `LIKE public.{table}` would fail because the tables wouldn't exist yet.

---

## 2. Signal: `profiles/signals.py` - `create_database_schema`

This signal fires every time a `Profile` object is saved. When a new profile is created, it creates a dedicated PostgreSQL schema for that user and seeds it with the public organisation data.

```python
@receiver(post_save, sender=Profile, dispatch_uid="create_database_schema")
```
- Registers this function to run after every `Profile.save()`. `dispatch_uid` prevents the signal from being registered twice (e.g. if the module is imported multiple times).

```python
def create_database_schema(sender, instance, created, **kwargs):
```
- `sender`: the model class (`Profile`). `instance`: the actual Profile object. `created`: `True` if this is a brand new profile, `False` if it's an update.

```python
    if not created:
        return
```
- Only create a schema for new users. If someone just updates their profile name, skip.

```python
    if settings.ENVIRONMENT != "prod":
        return
```
- Only run schema partitioning in production. In local dev (SQLite), this is skipped.

```python
    logger.info(f"Creating database schema for user {instance.email}")
```
- Log that we're about to create a schema. Useful for debugging.

```python
    schema_name = f"user_{instance.id}"
```
- The schema name follows the pattern `user_<profile_id>`. For user with id 2, the schema is `user_2`.

```python
    quoted_schema = connection.ops.quote_name(schema_name)
```
- Safely quotes the schema name for use in SQL. Prevents SQL injection and handles special characters. Wraps it in double quotes: `"user_2"`.

```python
    tables = [
        "venues_venue",
        "venues_venuecontact",
        "festivals_festival",
        "festivals_festivalcontact",
        "residencies_residency",
        "residencies_residencycontact",
    ]
```
- Same list of tenant tables as the migration. These are the only tables that get copied into the user's schema.

```python
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {quoted_schema}")
```
- Creates the user's schema (e.g. `CREATE SCHEMA IF NOT EXISTS "user_2"`). This is the PostgreSQL namespace that will hold their private copies of the tables.

```python
            for table in tables:
                quoted_table = connection.ops.quote_name(table)
```
- Iterate over each tenant table and quote its name for safe SQL usage.

```python
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {quoted_schema}.{quoted_table}
                    (LIKE template.{quoted_table} INCLUDING ALL)
                """)
```
- Creates the table in the user's schema using the `template` schema as a structural blueprint. For example: `CREATE TABLE IF NOT EXISTS "user_2"."venues_venue" (LIKE template."venues_venue" INCLUDING ALL)`. This copies columns, indexes, and constraints but no data.

```python
                cursor.execute(f"""
                    INSERT INTO {quoted_schema}.{quoted_table}
                    SELECT * FROM public.{quoted_table}
                """)
```
- Copies all rows from the `public` schema table into the user's schema table. This is the seeding step - it gives the user their starting pool of ~800 organisations. From this point on, the user's copy is independent; any changes they make only affect their schema.

```python
            logger.info(f"Schema {schema_name} created successfully for user {instance.email}")
    except Exception as e:
        logger.error(f"Failed to create schema {schema_name} for user {instance.email}: {e}")
        raise SchemaCreationError(f"Could not create schema for user {instance.id}") from e
```
- Log success or failure. If anything goes wrong (e.g. database connection issue), raise a `SchemaCreationError` so the failure is visible and the transaction can be rolled back.

---

## 3. Middleware: `clapp_backend/middleware.py` - `TenantMiddleware`

This middleware runs on every HTTP request. For authenticated users in production, it switches the PostgreSQL `search_path` to point at the user's schema so all ORM queries hit the user's private data.

```python
class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
```
- Standard Django middleware init. `get_response` is the next middleware or the view itself. Called once at startup.

```python
        self.use_tenant_partitioning = settings.ENVIRONMENT == "prod"
```
- Cache whether we're in prod. In local dev, tenant partitioning is disabled and everything reads/writes to the default `public` schema.

```python
    def __call__(self, request):
        if request.user.is_authenticated and self.use_tenant_partitioning:
```
- Only switch schemas for logged-in users in production. Anonymous requests (login page, public endpoints) use the default `public` schema.

```python
            schema = f"user_{request.user.id}"
            set_tenant_schema(schema)
```
- Build the schema name from the user's ID and store it in thread-local storage (see db_router.py below). This makes the schema name available to any code running in this request's thread.

```python
            try:
                with connection.cursor() as cursor:
                    quoted_schema = connection.ops.quote_name(schema)
                    cursor.execute(f"SET search_path TO {quoted_schema}, public")
```
- The critical line. `SET search_path TO "user_2", public` tells PostgreSQL: "when I query a table, look in `user_2` first, then fall back to `public`."
- For tables that exist in the user's schema (venues, festivals, residencies), PostgreSQL uses the user's copy.
- For tables that only exist in `public` (auth_user, profiles, applications), PostgreSQL falls through to `public`.
- This is why user isolation works transparently with the Django ORM - no code changes needed in views or models.

```python
            except Exception as e:
                logger.error(f"Failed to set schema for user {request.user.id}: {e}")
                raise
```
- If we can't set the schema, raise the error and abort the request. This prevents accidentally serving another user's data.

```python
        try:
            response = self.get_response(request)
        finally:
```
- Process the actual request (views, serializers, etc.). The `finally` block ensures cleanup always runs, even if the view throws an exception.

```python
            if self.use_tenant_partitioning:
                set_tenant_schema("public")
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("SET search_path TO public")
                except Exception:
                    pass
```
- After the request is done, reset the search_path back to `public`. This prevents schema leaking between requests on the same database connection (Django uses connection pooling). The `except: pass` is intentional - if we can't reset, the connection will be recycled anyway, and we don't want cleanup errors to mask the real response.

```python
        return response
```
- Return the response to the client.

---

## 4. Database Router: `clapp_backend/db_router.py`

The database router provides thread-local storage for the current tenant schema name and tells Django which database to use (always `default`).

```python
from threading import local

_thread_locals = local()
```
- Creates a thread-local storage object. Each thread (i.e. each request in a WSGI server) gets its own isolated copy of any attributes set on `_thread_locals`. This prevents one request's schema from leaking into another request running concurrently on a different thread.

```python
def set_tenant_schema(schema_name):
    _thread_locals.schema = schema_name
```
- Stores the current schema name for this thread. Called by the middleware at the start and end of each request.

```python
def get_tenant_schema():
    return getattr(_thread_locals, "schema", "public")
```
- Retrieves the current schema name for this thread. Returns `"public"` as a default if no schema has been set (e.g. during management commands or background tasks).

```python
class TenantRouter:
    def db_for_read(self, model, **hints):
        return "default"

    def db_for_write(self, model, **hints):
        return "default"
```
- Tells Django to always use the `default` database for reads and writes. Schema switching happens at the PostgreSQL level (via `search_path`), not at the Django database routing level.

```python
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == "default"
```
- Only allow migrations on the `default` database. This means `manage.py migrate` only runs against the `public` schema. User schemas get their tables via the signal's `CREATE TABLE ... LIKE` approach, not via Django migrations.

---

## How it all fits together

```
User signs up
    -> Profile.save() fires post_save signal
    -> create_database_schema() runs:
        1. CREATE SCHEMA "user_5"
        2. For each tenant table:
           a. CREATE TABLE "user_5"."venues_venue" (LIKE template."venues_venue")
           b. INSERT INTO "user_5"."venues_venue" SELECT * FROM public."venues_venue"
        3. User now has their own copy of all ~800 organisations

User makes a request
    -> TenantMiddleware.__call__() runs:
        1. SET search_path TO "user_5", public
        2. All Django ORM queries now hit user_5's tables for orgs, public for everything else
        3. After the response, search_path resets to public

User adds/edits/deletes an organisation
    -> Change only affects "user_5"."venues_venue" (etc.)
    -> Other users are unaffected
    -> Public schema is untouched
```
