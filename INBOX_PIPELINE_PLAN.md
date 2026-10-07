# Plan: Inbox → Application status pipeline

## Goal
Read incoming emails on `info@philippeducasse.com`. Detect emails about applications and suggest
status updates on `Application`. **Every update needs manual approval** (including auto-replies).
The design is personal-use first, but it should be possible to add more users later.

## Status
| Step | | |
|---|---|---|
| Header matching (commit 1769a39) | ✅ done | in production |
| 1. Pre-filter | ✅ done | backend, not deployed yet |
| 2. Candidate search | ✅ done | backend, not deployed yet |
| 3. Keyword gate | ✅ done | backend, not deployed yet |
| 4. Classification | ✅ done | backend, not deployed yet |
| 5. Model changes | ✅ done | migration `0016_inbound_email_unmatched` |
| 6. API | ✅ done | backend, not deployed yet |
| 7. Frontend | ⏳ todo | |
| 8. Tests | ✅ done for steps 1–6 | `test_inbox.py`, `test_matching.py` |
| 9. Docs | ⏳ todo | `apps/backend/docs/inbox_pipeline.md` still describes header matching only |

**Before deploying:** test migration `0016` on a copy of the prod database (it fills
`InboundEmail.profile` from existing rows), and make sure a `Profile` with the same email as
`IMAP_USERNAME` exists. Without it only `HEADER` matching runs.

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
were discarded. That lost new threads started by organisers, responses to applications made
through online forms, and organisers reaching out directly.

## Matching without a Message-ID

### 1. Pre-filter ✅ (`is_skipped` in `applications/inbox.py`, no LLM, not stored)
Skip:
- mailing lists / bulk: `List-Id`, `List-Unsubscribe`, `Precedence: bulk|list|junk`
- bounces: sender `mailer-daemon@…` / `postmaster@…`
- own messages: sender == `IMAP_USERNAME` (case-insensitive)

**Auto-replies are NOT skipped.** `is_auto_reply` recognises them from the headers
(`Auto-Submitted` other than `no`, `X-Autoreply`, `X-Autorespond`).

### 2. Candidate search ✅ (`applications/matching.py`)
`find_candidates(message, profile) -> Candidates(method, applications, organisations)`.
In order, stop at the first method that finds something:

| `match_method` | Rule | Applications searched |
|---|---|---|
| `HEADER` | `In-Reply-To`/`References` contains `Application.sent_message_id` | any |
| `SENDER` | sender address (case-insensitive) in `Application.email_recipients` or a Festival/Venue/Residency contact email | profile's, not deleted |
| `DOMAIN` | sender domain == `normalize_domain(website_url)` or the domain of a contact email. Free-mail domains (`FREE_MAIL_DOMAINS`) never match | profile's, not deleted |
| `NAME` | normalised organisation name appears as a whole phrase in the subject or first 2,000 chars of the body. Names under 5 characters and `GENERIC_NAMES` are ignored | profile's, **created in the last 365 days, including `DRAFT`** |
| `NONE` | nothing found | — |

Differences from the original plan:
- `NAME` uses "created in the last 365 days" instead of "current + previous season", because
  seasons are free text and not every application has one.
- Matching only uses the inbox owner's data: `inbox_profile()` = the `Profile` whose email is
  `IMAP_USERNAME`.
- Organisations found without an application are returned in `Candidates.organisations` and
  stored on unmatched emails so "Create application" can prefill them.
- Subject matching is dropped: if the subject still matches, it is a reply and `HEADER` catches it.
- `organisations.utils.normalize_domain` was fixed (it turned `www.x.org` into `.x.org`) and is
  now used here.

### 3. Keyword gate ✅ (`mentions_keyword` in `applications/inbox.py`)
Only emails with `match_method == NONE` go through this check. Subject + first 5,000 chars of the
body, accents removed, must contain a keyword (EN/DE/FR/ES/IT/NL), otherwise the email is
discarded **without calling Mistral**.
- `KEYWORD_STEMS` match the start of a word (`festival` → festivals, `program` → programme,
  Programm, programmation…).
- `KEYWORD_WORDS` are short words that must match a whole word, with an optional plural "s"
  (`show` must not match "shower").
- Left out on purpose: `fee` (feedback), `gig` (gigabyte), `appl` (Apple).

### 4. Classification ✅ (`classify` / `choose_application` in `applications/inbox.py`)
One Mistral call per kept email, including `HEADER` matches.
```python
class EmailClassification(BaseModel):
    is_application_related: bool
    application_id: Optional[int]        # chosen among candidates, None if no candidate fits
    suggested_status: Optional[StatusLiteral]
    is_auto_reply: bool
    summary: str
```
Prompt input: the email (sender with display name, subject, body), the candidate applications
(id, organisation, season, status, application date, start of the original application email:
3,000 chars for one candidate, 500 for several) and organisations found without an application.

Prompt rules:
- Confirmation that an application was received, for a `DRAFT` application → `APPLIED`.
- Auto-reply to an `APPLIED` application → `AUTO_REPLY_RECEIVED`.
- Never move an application backwards (order: DRAFT, APPLIED, AUTO_REPLY_RECEIVED,
  IN_DISCUSSION, final answer). Use `null` instead. This is only a prompt rule, not checked in code.
- Out-of-office replies: put the return date in the summary.

After the call:
- `HEADER` match: the application is already known. The LLM's `application_id` is ignored.
- Other methods: the LLM's `application_id` must be one of the candidates (an invented id is
  rejected) and `is_application_related` must be true → `PENDING_REVIEW`.
- No application chosen and `is_application_related` → `UNMATCHED` (`match_method = NONE`).
  Otherwise the email is discarded.
- `is_auto_reply` = header flag OR the LLM's answer.
- `received_at` is empty when the email has no `Date` header (imap-tools returns 1900-01-01).

### 5. Model changes ✅ (migration `0016_inbound_email_unmatched`)
- `APPLICATION_STATUS`: added `("AUTO_REPLY_RECEIVED", "Auto-reply received")` between
  `APPLIED` and `IN_DISCUSSION`. **Still missing in the frontend** (step 7).
- `InboundEmail`:
  - `profile` (FK, required), **not in the original plan**: unmatched emails have no
    application, so ownership can't come from `application.profile` any more. The migration
    fills it from existing rows.
  - `application` → nullable
  - `match_method`: `HEADER` / `SENDER` / `DOMAIN` / `NAME` / `NONE`
  - `is_auto_reply` (bool)
  - `organisation` (generic FK via `organisation_content_type` + `organisation_id`, nullable)
  - `state`: added `UNMATCHED`
- `email_recipients` is compared in lowercase (not lowercased when saving).
- Admin: `match_method` column, filters on `state`, `match_method`, `is_auto_reply`.

### 6. API ✅ (`InboundEmailViewSet` in `applications/views.py`)
- The list is scoped by `InboundEmail.profile`, filterable by `state` (incl. `UNMATCHED`) and
  `application`.
- Serializer: `organisation_name` (from the application, or the email's organisation),
  `organisation_type` (`festival` / `venue` / `residency`), `organisation_id`,
  `application_status` (null without an application).
- `POST /inbound-emails/{id}/approve/` with optional `status`: 400 if the email has no application.
- `POST /inbound-emails/{id}/link/` `{application_id, approve?, status?}`: attaches the email to
  one of the user's applications and sets `PENDING_REVIEW`. With `approve: true` the status is
  applied at once. 400 for a missing id or another user's application. Used to fix a wrong
  match, to resolve an `UNMATCHED` email and after "Create application".
- `POST /inbound-emails/{id}/dismiss/`: unchanged.
- "Create application" needs no new endpoint: the frontend calls `POST /applications/`, then
  `link` with `approve: true`.

### 7. Frontend ⏳
- Review queue shows: the `match_method` badge (HEADER = sure, SENDER/DOMAIN/NAME = check),
  an "Auto-reply" badge, and a "Draft application" hint when approving moves a `DRAFT` to `APPLIED`.
- "Change application" action on each email → picker → `link`.
- Unmatched tab (`state=UNMATCHED`) with:
  - **Create application**: opens the manual application form
    (`ManualApplicationForm` / `applications/create`) prefilled with the organisation
    (`organisation_type` + `organisation_id`, if found), status = suggested status,
    method = `EMAIL`, comments = summary. On save → `link` with `approve: true`.
    This covers organisers reaching out directly.
  - **Link to existing application** → picker → `link`.
  - **Dismiss**.
- `AUTO_REPLY_RECEIVED` added to status filters, labels and colours.

### 8. Tests ✅ (Mistral mocked)
- `applications/tests/test_matching.py`: each matching method, free-mail domains, partial and
  generic names, old applications, other users' data, deleted applications.
- `applications/tests/test_inbox.py`: pre-filter (`newsletter.eml`, `auto_reply.eml`, bounces,
  own messages), keyword gate in six languages plus false positives, import with candidates,
  invented `application_id`, `UNMATCHED` storage, inbox owner missing, `match_method` /
  `is_auto_reply`, prompt contents, API (`approve` without an application, `link`, link + approve,
  other users' applications, unmatched list).
- `organisations/tests/test_utils.py`: `normalize_domain`.
- Not covered: migration `0016` filling `profile` on existing rows.

### 9. Docs ⏳
Update `apps/backend/docs/inbox_pipeline.md` (how it works, matching table, API, limitations).

## Later (not needed for this feature)
- `MailboxConnection` per profile (provider, host, credentials, `last_uid`, `enabled`) and
  incremental fetch by UID. For now: env vars + last `DAYS_TO_CHECK` days + dedup on `message_id`.
- Gmail/Outlook readers (need read scopes and re-consent).
- Audit fields: `confidence`, `llm_model`, `prompt_version`, `raw_llm_response`, `reviewed_at`,
  `final_status`.
- Auto-approving auto-replies (for now every suggestion needs approval).
- Possibly apply the keyword gate to `DOMAIN` matches too, so that personal mail from someone at
  a known organisation is not sent to Mistral.

## Open points
1. Keyword list: check it against real mail. `tour` and `stage` are the broadest words.
2. Minimum name length and `GENERIC_NAMES` for `NAME` matching: tune them on real data.
