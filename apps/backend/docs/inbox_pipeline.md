# Inbox: application replies

Reads replies to application emails and suggests a new status for the application.
Nothing changes until you approve the suggestion.

## How it works

1. When an application email is sent, its `Message-ID` is saved in `Application.sent_message_id`
   (`organisations/emails.py`).
2. Every 10 minutes Celery runs `check_inbox` (`applications/inbox.py`). It reads the last 3 days
   of the inbox over IMAP.
3. An email is kept only if its `In-Reply-To` or `References` header contains a saved
   `sent_message_id`. Emails that were already imported are skipped.
4. Mistral reads the reply and suggests a status and a one-line summary. These are saved as an
   `InboundEmail` with state `PENDING_REVIEW`.
5. You approve (the status is applied and the summary is added to the comments) or dismiss it.

## Files

| File | What it does |
|---|---|
| `applications/inbox.py` | Fetch emails, match them to applications, ask Mistral |
| `applications/tasks.py` | Celery task, scheduled in `clapp_backend/celery.py` |
| `applications/models.py` | `InboundEmail` |
| `applications/services.py` | `set_application_status`, used by approval and the status endpoint |
| `applications/views.py` | `InboundEmailViewSet` |

## API

| Method | URL | |
|---|---|---|
| GET | `/api/inbound-emails/?state=PENDING_REVIEW` | Emails waiting for review |
| POST | `/api/inbound-emails/{id}/approve/` | Applies `suggested_status`, or `{"status": "..."}` from the body |
| POST | `/api/inbound-emails/{id}/dismiss/` | |

## Setup

Environment variables: `IMAP_USERNAME`, `IMAP_PASSWORD`, optional `IMAP_HOST` (default
`ssl0.ovh.net`), plus `MISTRAL_API_KEY` / `MISTRAL_DEFAULT_MODEL`.

Run a Celery worker and beat (`celery_worker` / `celery_beat` in `docker/docker-compose.yml`).
To check by hand: `python manage.py shell -c "from applications.inbox import check_inbox; check_inbox()"`.

## Limitations

- Only replies that keep the original `Message-ID` in their headers are found. Still to verify:
  Brevo must not rewrite the `Message-ID`.
- Automatic replies are imported too. Mistral should leave `suggested_status` empty for them; dismiss them.

## Tests

`uv run pytest applications/tests/test_inbox.py`. Sample emails are in `applications/tests/emails/`.
