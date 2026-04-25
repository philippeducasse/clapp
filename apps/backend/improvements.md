# Codebase Architecture Improvements

## Silent bugs (fix before any refactor)

### 1. `ResidencyViewSet` missing `get_queryset()` override
**File:** `organisations/residencies/views.py`

`ResidencySerializer` declares `has_application_this_year` and `current_year_application` fields but the view never annotates or prefetches them. These fields always return null at runtime.

### 2. `create_form_application()` silently drops the organisation FK
**File:** `organisations/services.py` (~line 410)

Passes `organisation=organisation` to `Application.objects.create()`, but `organisation` is a `GenericForeignKey` descriptor, not a real database field. Django silently ignores it. Form applications are created with `content_type=NULL, object_id=NULL`.

---

## Deepening opportunities

### 1. The `organisations/services.py` god module
**File:** `organisations/services.py` (550 lines)

**Problem:** This module does five fundamentally different things: LLM prompt construction, email assembly, email dispatch, application record creation, and input validation. Its interface is as complex as its implementation — callers must understand all five concerns to know what `prepare_application_email()` does vs `create_form_application()` vs `validate_application_recipients()`. It is a shallow module: delete it and the complexity reappears across five call sites in `views.py`, not concentrated anywhere useful. Testing any one function imports the whole module, including live SMTP configuration and GenericFK logic.

**Solution:** Split into three focused modules by responsibility seam:
1. `emails.py` — email construction and dispatch
2. `prompts.py` — all LLM prompt generation
3. `applications.py` — application record creation and input validation

Each module would be deep: a small interface hiding the logic that belongs there.

**Benefits:** Tests for email construction no longer need to import LLM prompt logic. Tests for application creation no longer need to patch SMTP. Each module can be understood and tested in isolation. Locality: a bug in email formatting is always found in `emails.py`.

---

### 2. Serializer duplication across the three organisation types
**Files:** `organisations/festivals/serializers.py`, `organisations/venues/serializers.py`, `organisations/residencies/serializers.py`

**Problem:** All three serializers copy-paste an identical `update()` body: pop `contacts_data`, call `super().update()`, call `handle_nested_contacts()`. Festival and Residency serializers additionally copy the same `has_application_this_year` field declarations and `get_current_year_application()` method — but only the Festival view populates them, making the Residency version dead. The interface of `OrganisationSerializer` (the base) promises nothing about contact handling, so every subclass re-implements it independently. Apply the deletion test: delete `update()` from all three — the identical complexity reappears across three files. That's a sign the base serializer should own it.

**Solution:** Move the `update()` body into a base `OrganisationSerializer` mixin that owns the `contacts_data` dance. Move `has_application_this_year` / `get_current_year_application()` into the same mixin, then align `ResidencyViewSet.get_queryset()` to actually populate it (fixing silent bug #1 above simultaneously).

**Benefits:** Adding a fourth organisation type (e.g. Workshop) gets correct contact handling for free. The `has_application_this_year` logic has one home. Tests for update-with-contacts can be written once against the base serializer.

---

### 3. `ApplicationSerializer`'s isinstance dispatch chain
**File:** `applications/serializers.py` — `ApplicationSerializer.to_representation()`

**Problem:** `to_representation()` checks `isinstance(organisation, Festival)` / `isinstance(organisation, Venue)` / `isinstance(organisation, Residency)` and dispatches to three different full nested serializers. Adding a fourth organisation type is an edit to the serializer. The interface of `ApplicationSerializer` is as complex as its implementation: understanding what it returns requires reading all three downstream serializers. The three downstream serializers each trigger their own prefetch/annotation pipelines, creating N-query risk when listing applications with many different organisation types.

**Solution:** Add a `get_serializer_class()` classmethod to each organisation model (or a type registry dict keyed on `ContentType`) so `ApplicationSerializer.to_representation()` becomes one lookup: `serializer_class = organisation._meta.model.serializer_class`. The seam moves to the model/registry; adding a new type no longer touches the application serializer at all.

**Benefits:** Leverage: the application serializer no longer imports from three separate apps. Locality: the mapping from organisation type to serializer class lives in one place. Tests for a new organisation type don't require touching `ApplicationSerializer`.

---

### 4. The `apply()` action: application record created before email sent
**File:** `organisations/views.py` — `OrganisationViewSet.apply()`

**Problem:** The view creates the `Application` DB record (status `"APPLIED"`) and then calls `send_application_email()`. If the email dispatch raises — wrong SMTP credentials, network error, anything — the application is committed with `status="APPLIED"` but no email was sent. The user has no way to distinguish "submitted and delivered" from "saved but never sent." There is no compensating transaction and no retry mechanism. The seam between "record the intent" and "execute the intent" does not exist.

**Solution:** Introduce a separate `email_sent` boolean field (or `status="EMAIL_FAILED"` variant) on `Application`, set it after `send_application_email()` succeeds. On failure, catch the exception, update `status="EMAIL_FAILED"`, and surface a 503 with a clear message. This separates the two concerns at a real seam: persistence vs delivery.

**Benefits:** Locality: the email-failure path is visible in the data. Testability: integration tests can assert that a failed email send leaves `status="EMAIL_FAILED"` rather than silently passing. Users can be shown accurate submission state.

---

## Other findings

### Dead code
- `services/tests/test_gemini_service.py` is entirely commented out. The Gemini integration is gone; the file should be deleted.
- `generate_enrich_prompt()` in `organisations/services.py` (~line 90) is the generic fallback version, never called — all three subclasses override `get_enrich_prompt()` with type-specific versions, and `OrganisationViewSet` is never instantiated directly.

### Security
- `FIELD_ENCRYPTION_KEY` in `clapp_backend/base.py` has a hardcoded fallback Fernet key. A deployment that omits the `FERNET_KEY` env var will encrypt `email_host_password` and OAuth tokens with a publicly known key, with no error raised.

### Misleading naming
- The `tenant_schema` parameter in `MistralClient.chat()` and the rate limiter is actually a user ID integer, not a PostgreSQL schema name. A `TODO` comment in `organisations/views.py` acknowledges this. The parameter should be renamed to `user_id`.