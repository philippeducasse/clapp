# Inbox: emails about applications

Reads incoming emails on the inbox (`IMAP_USERNAME`), finds the ones about applications and
suggests a new status. **Nothing changes until you approve the suggestion**, including for
auto-replies.

## How it works

Every 10 minutes Celery runs `check_inbox` (`applications/inbox.py`). It reads the last 3 days of
the inbox over IMAP and skips emails that were already imported (dedup on `Message-ID`). Matching
only uses the data of the inbox owner: the `Profile` whose email is `IMAP_USERNAME`. Without that
profile only `HEADER` matching runs.

For each email:

1. **Pre-filter** (`is_skipped`, not stored): mailing lists / bulk mail (`List-Id`,
   `List-Unsubscribe`, `Precedence: bulk|list|junk`), bounces (`mailer-daemon@`, `postmaster@`) and
   our own messages are skipped. Auto-replies are kept and flagged (`is_auto_reply`, from
   `Auto-Submitted`, `X-Autoreply`, `X-Autorespond`).
2. **Candidate search** (`applications/matching.py`, `find_candidates`). The first method that finds
   something wins:

   | `match_method` | Rule | Applications searched |
   |---|---|---|
   | `HEADER` | `In-Reply-To`/`References` contains `Application.sent_message_id` | any |
   | `SENDER` | sender in `Application.email_recipients` or an organisation contact email | owner's, not deleted |
   | `DOMAIN` | sender domain == organisation website domain or contact email domain. Free-mail domains never match | owner's, not deleted |
   | `NAME` | organisation name (≥ 5 chars, not in `GENERIC_NAMES`) appears as a phrase in the subject or first 2,000 chars of the body | owner's, created in the last 365 days, including drafts |
   | `NONE` | nothing found | — |

   Organisations found without an application are kept to prefill "Create application".
3. **Keyword gate** (`mentions_keyword`), only for `NONE`: subject + first 5,000 chars of the body
   must contain an application-related keyword (EN/DE/FR/ES/IT/NL). Otherwise the email is dropped
   without calling Mistral.
4. **Classification** (`classify`): one Mistral call (`chat.parse`, `EmailClassification` schema)
   with the email, the candidate applications and organisations. It returns
   `is_application_related`, `application_id`, `suggested_status`, `is_auto_reply` and a summary.
   - `HEADER`: the application is already known, the LLM's `application_id` is ignored.
   - Other methods: the `application_id` must be one of the candidates → `PENDING_REVIEW`.
   - No application but related → `UNMATCHED`. Otherwise the email is dropped.
   - Prompt rules: receipt confirmation for a `DRAFT` → `APPLIED`; auto-reply to `APPLIED` →
     `AUTO_REPLY_RECEIVED`; never move backwards (prompt only, not enforced in code);
     out-of-office return dates go in the summary.
5. **Review** in the dashboard ("Replies to review" card):
   - *To review* tab: match method badge (`Reply` = certain, sender/domain/name = check), an
     "Auto-reply" badge, a warning when approving moves a draft to applied. Actions: apply status,
     change application, dismiss. The application page shows its own pending emails.
   - *Unmatched* tab: create application (opens `/applications/create?inboundEmail=<id>`, prefilled
     with organisation, suggested status, method `EMAIL` and the summary as comments; on save the
     email is linked and approved), link to an existing application, dismiss.

Approving applies the status and adds the summary to the application's comments (once).

## Files

| File | What it does |
|---|---|
| `applications/inbox.py` | Fetch, pre-filter, keyword gate, Mistral classification, storage |
| `applications/matching.py` | Candidate search |
| `applications/tasks.py` | Celery task, scheduled in `clapp_backend/celery.py` |
| `applications/models.py` | `InboundEmail`, `APPLICATION_STATUS` (incl. `AUTO_REPLY_RECEIVED`) |
| `applications/services.py` | `set_application_status`, used by approval and the status endpoint |
| `applications/views.py` | `InboundEmailViewSet` |
| frontend `InboundEmailsCard.tsx`, `ApplicationPicker.tsx`, `ManualApplicationForm.tsx` | Review UI |

## `InboundEmail`

`profile` (owner), `application` (nullable), `match_method`, `is_auto_reply`, `organisation`
(generic FK, for unmatched emails), `message_id`, `from_address`, `subject`, `body`, `received_at`
(empty without a `Date` header), `suggested_status`, `summary`, `state`
(`PENDING_REVIEW` / `UNMATCHED` / `APPROVED` / `DISMISSED`).

## API

All scoped to the logged-in user's profile.

| Method | URL | |
|---|---|---|
| GET | `/api/inbound-emails/?state=PENDING_REVIEW&application=<id>` | List, filter by `state` and `application` |
| GET | `/api/inbound-emails/{id}/` | One email |
| POST | `/api/inbound-emails/{id}/approve/` | Applies `suggested_status` or `{"status"}`. 400 without an application |
| POST | `/api/inbound-emails/{id}/link/` | `{application_id, approve?, status?}`: attach to one of your applications (→ `PENDING_REVIEW`), optionally approve at once |
| POST | `/api/inbound-emails/{id}/dismiss/` | |

The serializer adds `organisation_name`, `organisation_type` (`festival`/`venue`/`residency`),
`organisation_id` and `application_status`. "Create application" uses `POST /api/applications/`
followed by `link` with `approve: true`.

## Setup

Environment variables: `IMAP_USERNAME`, `IMAP_PASSWORD`, optional `IMAP_HOST` (default
`ssl0.ovh.net`), plus `MISTRAL_API_KEY` / `MISTRAL_DEFAULT_MODEL`. A `Profile` with the same email
as `IMAP_USERNAME` must exist.

Run a Celery worker and beat (`celery_worker` / `celery_beat` in `docker/docker-compose.yml`).
To check by hand: `python manage.py shell -c "from applications.inbox import check_inbox; check_inbox()"`.

## Limitations

- Single inbox from env vars, last 3 days only (no per-user mailbox, no incremental UID fetch).
- Gmail/Outlook OAuth only has send scopes; reading those inboxes needs new scopes and re-consent.
- "Never move backwards" is only a prompt rule.
- `DOMAIN` matches skip the keyword gate, so personal mail from someone at a known organisation
  goes to Mistral.
- The keyword list, minimum name length and `GENERIC_NAMES` still need tuning on real mail.

## Tests

`uv run pytest applications/tests/test_inbox.py applications/tests/test_matching.py`
(Mistral is mocked). Sample emails are in `applications/tests/emails/`. Migration `0016` filling
`profile` on existing rows is not covered.
