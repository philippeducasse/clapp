# Plan: Inbox → Application status pipeline

## Goal
Read incoming emails on `info@philippeducasse.com`. Detect emails about applications and suggest
status updates on `Application`. **Every update needs manual approval** (including auto-replies).
The design is personal-use first, but it should be possible to add more users later.

## Context
- Outgoing application emails are sent by the app through the **Brevo SMTP relay**
  (`organisations/emails.py`). Brevo only sends mail and plays no part in receiving it.
- The inbox is hosted with **OVHcloud** and read over IMAP (`ssl0.ovh.net:993`).
- Sent mail does not land in the OVH Sent folder. The app records the `Message-ID` of outgoing
  mail itself.
- The existing Gmail/Outlook OAuth only has **send** permissions. Reading those inboxes later
  needs `gmail.readonly` / `IMAP.AccessAsUser.All` (or `Mail.Read`) and users would have to re-consent.
- Available: Celery + Redis, the Mistral SDK in `services/mistral_service.py`, `normalize_domain`
  in `organisations/utils.py`.
- No LangChain: one structured LLM call per email (`client.chat.parse` with a Pydantic schema).

## Done (commit 1769a39)
- `applications/services.py`: `set_application_status(application, new_status, note=None)`.
- `Application.sent_message_id`, saved when the app sends an application email.
  Checked in prod: Brevo keeps our `Message-ID`, and replies are matched.
- `InboundEmail` model (`application`, `message_id`, `from_address`, `subject`, `body`,
  `received_at`, `suggested_status`, `summary`, `state`).
- `applications/inbox.py`: IMAP fetch of the last 3 days (`imap-tools`), header matching,
  Mistral classification, dedup on `message_id`.
- Celery beat task `check_inbox_task` every 10 min.
- API: `GET /api/inbound-emails/`, `POST .../approve/`, `POST .../dismiss/`.
- Review queue in the dashboard.

**Limitation addressed below:** emails without our `Message-ID` in `In-Reply-To`/`References`
are discarded. That loses new threads started by organisers, responses to applications made through
online forms, and organisers reaching out directly.

## Next: matching without a Message-ID

### 1. Pre-filter (no LLM, not stored)
Skip:
- mailing lists / bulk: `List-Id`, `List-Unsubscribe`, `Precedence: bulk|list`
- bounces: sender `mailer-daemon@…` / `postmaster@…`
- own messages: sender == `IMAP_USERNAME`

**Auto-replies are NOT skipped** (`Auto-Submitted: auto-replied`, `X-Autoreply`, `X-Autorespond`).
They go through matching like any other email and are flagged (see step 4).

### 2. Candidate search (`find_candidates(message) -> (match_method, list[Application])`)
In order, stop at the first method that finds something:

| `match_method` | Rule | Applications searched |
|---|---|---|
| `HEADER` | `In-Reply-To`/`References` contains `Application.sent_message_id` (existing) | — |
| `SENDER` | sender address (lowercased) in `Application.email_recipients` or an organisation `*Contact.email` | not deleted |
| `DOMAIN` | `normalize_domain(sender)` == domain of organisation `website_url` or of a contact email. Free-mail domains (gmail.com, gmx.de, web.de, outlook.com, hotmail.*, yahoo.*, icloud.com, …) never match | not deleted |
| `NAME` | normalised organisation name appears in the subject or first ~2k chars of the body. Names below a minimum length / generic words are ignored | current + previous season, **including `DRAFT`** |
| `NONE` | nothing found | — |

- Organisations are Festival / Venue / Residency (generic FK on `Application`). Search the
  contacts of all three types.
- If an organisation is found but has no application, keep it on the email (`organisation`) so
  that "Create application" can prefill it.
- `NAME` covers form confirmations ("Thank you for your application to *Fringe XY*") for
  applications made outside the app, which are still `DRAFT`.
- Subject matching (the old idea) is dropped: if the subject still matches, it is a reply and `HEADER` catches it.

### 3. Keyword gate for unmatched emails
Only emails with `match_method == NONE` go through this check. If the subject + body contain none
of a multilingual keyword list (e.g. *festival, booking, programme/programm, show, spectacle,
performance, residency/résidence, application, candidature, Bewerbung, Anfrage, Gastspiel,
Auftritt, tour, …*), the email is discarded **without calling Mistral**. This stops personal mail from being sent to Mistral.
Keep the list in one constant in `applications/inbox.py`.

### 4. Classification (one Mistral call per kept email)
```python
class EmailClassification(BaseModel):
    is_application_related: bool
    application_id: Optional[int]        # chosen among candidates, None if no candidate fits
    suggested_status: Optional[StatusLiteral]
    is_auto_reply: bool
    summary: str
```
Prompt input: email (subject, sender, body), candidate applications (id, organisation, season,
current status, application date, start of the original message) and valid statuses.

Prompt rules:
- Confirmation that an application was received (form or auto-reply) for a `DRAFT` application → `APPLIED`.
- Auto-reply to an `APPLIED` application → `AUTO_REPLY_RECEIVED`.
- Never suggest moving an application backwards (e.g. from `IN_DISCUSSION`/`ACCEPTED` to
  `AUTO_REPLY_RECEIVED`). Use `null` instead. The email is still saved for information.
- Out-of-office replies: put the return date in the summary ("Away until 12 Oct").

After the call:
- `HEADER` match: the application is already known. `application_id` from the LLM is ignored.
- Candidates exist and the LLM picks one → `PENDING_REVIEW` with that application.
- Candidates exist but the LLM picks none, or no candidates: if `is_application_related` →
  `UNMATCHED`, otherwise discard.
- `is_auto_reply` = header flag OR the LLM's answer.

### 5. Model changes
- `APPLICATION_STATUS`: add `("AUTO_REPLY_RECEIVED", "Auto-reply received")` between `APPLIED`
  and `IN_DISCUSSION` (migration, plus the frontend status list, labels and colours).
- `InboundEmail`:
  - `application` → nullable
  - `match_method`: `HEADER` / `SENDER` / `DOMAIN` / `NAME` / `NONE`
  - `is_auto_reply` (bool)
  - `organisation` (generic FK via `content_type` + `object_id`, nullable): organisation found without an application
  - `state`: add `UNMATCHED`
- Compare `email_recipients` in lowercase (or lowercase them when saving).

### 6. API
- `POST /inbound-emails/{id}/link/` `{application_id}`: attach the email to an application.
  Used to fix a wrong fuzzy match, to resolve an `UNMATCHED` email, and after "Create application".
  The email then goes to `PENDING_REVIEW` (or `APPROVED` if `approve: true` is sent).
- `approve` / `dismiss`: no changes. Approve requires an application (400 if none).
- Allow filtering the list by `state=UNMATCHED`.

### 7. Frontend
- Review queue shows: the `match_method` badge (HEADER = sure, SENDER/DOMAIN/NAME = check),
  an "Auto-reply" badge, and a "Draft application" hint when approving moves a `DRAFT` to `APPLIED`.
- "Change application" action on each email → picker → `link`.
- Unmatched tab (`state=UNMATCHED`) with:
  - **Create application**: opens the manual application form
    (`ManualApplicationForm` / `applications/create`) prefilled with the organisation (if found),
    status = suggested status, method = `EMAIL`, comments = summary. On save → `link` + approve.
    This covers organisers reaching out directly.
  - **Link to existing application** → picker → `link`.
  - **Dismiss**.
- `AUTO_REPLY_RECEIVED` added to status filters, labels and colours.

### 8. Tests (`applications/tests/test_inbox.py`, `.eml` samples, Mistral mocked)
- new thread from a contact address → `SENDER`
- sender on the organisation's domain → `DOMAIN`
- gmail sender with an unknown address → no `DOMAIN` match
- form confirmation that names an organisation with a `DRAFT` application → `NAME`, suggests `APPLIED`
- auto-reply to an `APPLIED` application → kept, `is_auto_reply`, suggests `AUTO_REPLY_RECEIVED`
- direct enquiry from an unknown organisation with keywords → `UNMATCHED`
- personal mail without keywords → discarded, Mistral not called
- newsletter (`List-Id`) → skipped
- organisation with a short/generic name → no `NAME` match
- `link` endpoint, approve without an application → 400

### 9. Docs
Update `apps/backend/docs/inbox_pipeline.md` (how it works, matching table, limitations).

## Later (not needed for this feature)
- `MailboxConnection` per profile (provider, host, credentials, `last_uid`, `enabled`) and
  incremental fetch by UID. For now: env vars + last `DAYS_TO_CHECK` days + dedup on `message_id`.
- Gmail/Outlook readers (need read scopes and re-consent).
- Audit fields: `confidence`, `llm_model`, `prompt_version`, `raw_llm_response`, `reviewed_at`,
  `final_status`.
- Auto-approving auto-replies (for now every suggestion needs approval).

## Open points
1. Keyword list: fill in the languages actually used by organisers (EN/DE/FR/ES/IT/NL?).
2. Minimum name length and generic-word list for `NAME` matching: tune them on real data.
