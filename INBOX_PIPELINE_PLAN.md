# Plan: Inbox → Application status pipeline

## Goal
Read incoming emails on `info@philippeducasse.com`. Detect replies to applications and suggest
status updates on `Application`. **Every update needs manual approval.**
The design is personal-use first, but it should be possible to add more users later.

## Context
- Outgoing application emails are sent by the app through the **Brevo SMTP relay**
  (`profiles/emails.py`). Brevo only sends mail and plays no part in receiving it.
- The inbox is hosted with **OVHcloud** and read over IMAP (`ssl0.ovh.net:993`).
- Sent mail does not land in the OVH Sent folder. The app must record the `Message-ID` of
  outgoing mail itself.
- The existing Gmail/Outlook OAuth only has **send** permissions. Reading those inboxes later
  needs `gmail.readonly` / `IMAP.AccessAsUser.All` (or `Mail.Read`) and users would have to re-consent.
- Already available: Celery + Redis, the Mistral SDK (`mistralai==1.9.1`) in `services/mistral_service.py`,
  and `normalize_domain` in `organisations/utils.py`.
- No LangChain: there is a single structured LLM call per email. Use `client.chat.parse` with a Pydantic schema.
  Look at Pydantic AI later if this grows into an agent.

## Steps

### 0. Clean up the applications app
- Rename `ApplicationViewSet.tag` → `set_status` and fix its docstring
  ("Update the status of an application."). The URL `PATCH /applications/{id}/status/{new_status}/` stays the same.
- Add `applications/services.py` with
  `set_application_status(application, new_status, note=None)`: it validates the status against
  `APPLICATION_STATUS`, adds an optional note to `comments`, and saves. Called by `set_status`
  and by the approval step.
- Change the default of `Application.status` from `"NOT_APPLIED"` (not a valid choice) to `"DRAFT"`, with a migration.

### 1. Record outgoing Message-IDs
- Add `Application.sent_message_id` (CharField, indexed, blank).
- When the app sends an application email, set or capture `Message-ID` (`make_msgid`) and save it.
- **Check:** send a test through Brevo and confirm the received `Message-ID` is unchanged.
  If Brevo rewrites it, matching falls back to domain and subject.

### 2. Models
- `MailboxConnection` (FK Profile): provider (`IMAP` for now, later `GMAIL`/`OUTLOOK`), host, port,
  username, credentials (env vars for now, encrypted field later), `last_uid`, `enabled`.
- `InboundEmail`:
  - `message_id` (unique, so nothing is processed twice), `in_reply_to`, `references`
  - `from_address`, `subject`, `body_text`, `received_at`, `profile`, `mailbox`
  - `matched_application` (FK, nullable), `match_method` (`HEADER` / `DOMAIN` / `SUBJECT` / `LLM` / `NONE`)
  - `suggested_status`, `confidence`, `summary`
  - `llm_model`, `prompt_version`, `raw_llm_response` (JSON) for auditing and measuring accuracy
  - `state`: `PENDING_REVIEW` / `APPROVED` / `DISMISSED` / `NOT_RELEVANT`
  - `reviewed_at`, `final_status` (what the user actually applied)

### 3. Inbox readers (`applications/inbox/`)
- Interface: `fetch_since(mailbox) -> list[ParsedEmail]`.
- `ImapReader` using `imap-tools`. It reads new mail by UID and parses headers, plain-text body
  (quoted replies stripped, length truncated), `In-Reply-To` and `References`.
- Later: `GmailReader` / `OutlookReader`, reusing the token refresh code in `profiles/emails.py`.

### 4. Processing
- **Pre-filter (no LLM):** skip auto-replies, bounces, newsletters and own messages
  (`Auto-Submitted`, `X-Autoreply`, `List-Id`, `Precedence: bulk`, sender == self).
  These are saved as `NOT_RELEVANT`.
- **Matching, in order:**
  1. `In-Reply-To` / `References` against `Application.sent_message_id`
  2. Sender domain against organisation contacts / `email_recipients` (`normalize_domain`)
  3. Normalised subject (strip `Re:`/`AW:`/`Fwd:`…) against `email_subject`
  4. Otherwise the LLM chooses from candidates (current season, status `APPLIED` / `IN_DISCUSSION`)
- **Classify** (`services/mistral_service.py`): `client.chat.parse` with a Pydantic schema
  ```python
  class EmailClassification(BaseModel):
      is_application_response: bool
      application_id: int | None
      suggested_status: Literal[...APPLICATION_STATUS keys...] | None
      confidence: float
      summary: str
      is_auto_reply: bool
  ```
  Input: email body, the matched application's original message, organisation name and valid statuses.
- Save as `PENDING_REVIEW`. **The application is not changed at this stage.**

### 5. Celery tasks (`applications/tasks.py`)
- `poll_inboxes`, Celery beat every 10 min: for each enabled `MailboxConnection`, fetch new mail,
  create `InboundEmail` rows and queue `process_inbound_email.delay(id)`.
- `process_inbound_email(id)`: pre-filter → match → classify → save.
- Add `CELERY_BEAT_SCHEDULE` and make sure a beat process runs in Docker/prod.

### 6. Approval API
- `InboundEmailViewSet` (scoped to `request.user`), filterable by `state`.
- `POST /inbound-emails/{id}/approve/` with an optional `status` override and optional `application_id`
  correction → calls `set_application_status(..., note=summary)`, sets `APPROVED`.
- `POST /inbound-emails/{id}/dismiss/` → `DISMISSED`.

### 7. Frontend
- Review queue: the email next to the matched application, the suggested status (editable), the summary,
  and approve/dismiss buttons. Show the number waiting for review in the nav.

### 8. Tests
- Sample `.eml` files: header reply, domain-only reply, auto-reply, newsletter, unrelated mail.
- Mock the Mistral client. Test each matching step, the pre-filter, the approve/dismiss actions and
  `set_application_status`.

## Open points
1. Brevo `Message-ID` test (step 1).
2. Where IMAP credentials live: env vars for now vs encrypted in `MailboxConnection`.
3. Is Celery beat already running in production?
