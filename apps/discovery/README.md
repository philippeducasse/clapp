# clapp discovery service

Finds new festivals, residencies and venues from a **starting point** (a link, a request in plain
words, or both) and proposes them to superusers for review in clapp.

This service runs in its own container and has **no database**. Everything it finds is stored by
the backend's `discovery` Django app (`apps/backend/discovery`), which also handles the review
(accept / dismiss) and turns accepted candidates into seeds shared with every user.

See `DISCOVERY_PLAN.md` at the repo root for the full plan.

> **Status:** step 4 of the plan. The tools the graph will use (LLM models and budget, search,
> fetching, links, known-index matching, verification) exist and are tested, but the service still
> runs the **stub graph**: it posts a few progress lines and one fake candidate ("Stub festival
> (run N)"), then finishes. The real graph comes in step 5.

## How it fits together

```
browser ──► frontend (/discover, superusers only)
               │  /api/discovery/*        session auth, superusers only
               ▼
            backend (Django)   stores runs, candidates, sources; review; accept
               │  ▲
   POST /runs  │  │  /internal/discovery/*   Bearer DISCOVERY_SERVICE_TOKEN
               ▼  │  progress, known-index, candidates, sources
            discovery service (this app: FastAPI + background asyncio task)
```

- The **frontend only talks to the backend**. It never calls this service.
- The **backend calls this service once per run** (`POST /runs`), from
  `apps/backend/discovery/service_client.py`.
- **Everything after that goes from the service to the backend**, under `/internal/discovery/`:

  | Call | Backend view | Purpose |
  |---|---|---|
  | `PATCH runs/{id}/` | `update_run` | status, progress lines, counters, plan, errors. Also the heartbeat. Replies with `cancel_requested` |
  | `GET known-index/` | `get_known_index` | organisations clapp already has (seeds, superusers' organisations, all candidates) |
  | `POST runs/{id}/candidates/` | `create_candidates` | save candidates. The backend marks exact matches `ALREADY_KNOWN` |
  | `POST sources/` | `upsert_sources` | record artist and aggregator sites that produced leads |

- `/internal/` isn't routed by nginx or Next.js, so only containers on `clapp-network` can reach it.
  It also requires the shared token.

## Code layout

```
discovery/
  app.py             FastAPI app: POST /runs, GET /health. Creates the BackendClient and Runner at startup
  config.py          Settings (pydantic-settings), read from the environment and .env
  backend_client.py  BackendClient: typed async calls to /internal/discovery/*, plus the payload models
  runner.py          Runner (one run at a time), RunContext (what a graph uses), stub_graph
  llm.py             get_chat_model / get_structured_model, RunBudget (limits + LLM call counter), tracing
  tools/
    domains.py       domain_of, registrable_domain (tldextract, offline), same_site
    search.py        SearchProvider protocol; MistralSearch (web_search, keeps citation URLs)
    fetch.py         Fetcher: robots.txt, 1 request/s per domain, size cap, 30-day diskcache, trafilatura
    links.py         extract_links (same site), rank_links (multilingual keywords per goal)
    known.py         KnownIndex: is a lead already in clapp? (domain, registrable domain, fuzzy name)
    verify.py        blocklisted hosts, extract_emails, SeenContent + verified_emails/url/website
tests/
  conftest.py        settings fixture, FakeBackend (respx mock of /internal/discovery/*), fixture loaders
  fixtures/          saved HTML pages (artist home, calendar, festival contact, JavaScript-only page)
  test_app.py        HTTP endpoints: token, 202/409/422, shutdown
  test_runner.py     run lifecycle: DONE / CANCELLED / FAILED, backend client errors
  test_llm.py, test_search.py, test_fetch.py, test_links.py, test_known.py, test_verify.py
```

Coming in step 5: `prompts/` and `graph/` (the LangGraph workflow that replaces `stub_graph`).

## Tools (step 4)

- **Budget.** `RunBudget(settings, counters)` holds the per-run limits and shares the run's counters,
  so progress updates show what was spent. `spend("pages" | "searches" | "leads")` raises
  `BudgetExceeded` past the limit. Passed as a callback to chat models, it counts every LLM call and
  refuses the call past `MAX_LLM_CALLS` before it is sent. `max_hops_per_site` is enforced by
  `navigate` (step 5).
- **Models.** `get_chat_model(purpose, settings, budget)`: `classify`, `pick_link` and `pick_website`
  use `MISTRAL_SMALL_MODEL`; `interpret`, `extract_leads` and `extract_org` use `MISTRAL_LARGE_MODEL`.
  `get_structured_model(purpose, Schema, ...)` adds `.with_structured_output(Schema)`.
- **Search.** `MistralSearch.search(query, budget)` runs a Mistral conversation with the `web_search`
  tool and returns `SearchHit{url, title, snippet}` from the citations (bare URLs in the answer are
  only used when there are none). Errors raise `SearchError`.
- **Fetch.** `Fetcher.fetch(url, budget)` returns a `Page{url, final_url, status, title, html, text}`
  or raises `FetchError` (`reason`: `invalid_url`, `robots`, `network`, `http_status`, `not_html`).
  Cache hits count against the page budget too. `page.is_empty` means no readable text (usually a
  JavaScript-only site); it's logged as "empty content" and callers skip it. robots.txt follows
  RFC 9309: 4xx allows everything; 401/403, 5xx or no answer disallows the site.
- **Links.** `extract_links(html, url)` keeps same-site links (subdomains included) without files,
  `mailto:` or fragments; `rank_links(links, ["calendar" | "contact" | "application"])` scores
  them by keywords in the anchor text and URL path (en, fr, de, nl, es, it, pt), whole words only.
- **Known.** `KnownIndex.load(backend)` then `match(name, country, website_url)`. Domain matches
  ignore blocklisted hosts (a Facebook page isn't a domain). A name match needs rapidfuzz
  `token_sort_ratio` ≥ 90 in the same country, or an exact name when a country is missing.
  `add()` lets the graph dedupe leads within a run.
- **Verify.** Feed every fetched page and search citation into a `SeenContent`; then
  `verified_emails`, `verified_url` and `verified_website` keep only what was seen. Emails are
  found in text, `mailto:` links and simple `[at]`/`(dot)` obfuscation. `is_blocklisted` covers
  social networks, ticketing and listing sites, encyclopedias, news and file hosting: these are
  never an organisation's `website_url`.

## What happens at runtime

1. **Import.** `uvicorn discovery.app:app` imports `app.py`, whose last line runs `app = create_app()`.
   That reads the settings and registers the routes. No network calls happen yet.
2. **Startup.** FastAPI runs the first half of `lifespan` (up to `yield`): it creates one
   `BackendClient` and one `Runner`, and stores the runner on `app.state.runner`.
3. **`POST /runs {run_id, starting_point}`** from the backend:
   1. `require_token` checks `Authorization: Bearer <token>`. A missing or wrong token gets **401**.
   2. The body is validated against `RunRequest`. Invalid input gets **422**.
   3. `runner.start()` either raises `RunnerBusy`, which gets **409** (a run is already active), or schedules
      the run as an asyncio task and returns **202** straight away.
4. **The run** (`Runner._run`, in the background):
   1. `PATCH runs/{id}/` with `status=RUNNING`. The backend sets `started_at`.
   2. It runs the graph. Each `ctx.progress(step, message)` sends a PATCH with a progress line and the
      counters. If the reply has `cancel_requested: true`, it raises `RunCancelled`.
   3. It finishes with a PATCH:
      - `DONE` when the graph returns normally
      - `CANCELLED` after a cancel
      - `FAILED` with the error if anything raised
5. **Shutdown.** FastAPI runs the second half of `lifespan`: the active run is cancelled and reported
   `FAILED` ("discovery service shutting down"), and then the HTTP client is closed.

If the service dies without reporting, the backend notices the missing heartbeat. A `RUNNING` run with
no PATCH for 10 minutes is marked `FAILED` the next time it's read.

## Running locally

Requires [uv](https://docs.astral.sh/uv/).

```bash
cd apps/discovery
uv sync
cp .env.example .env          # then set DISCOVERY_SERVICE_TOKEN
uv run fastapi dev discovery/app.py --port 8001
```

The backend needs the same token and the service URL, in `apps/backend/.env`:

```
DISCOVERY_SERVICE_URL=http://localhost:8001
DISCOVERY_SERVICE_TOKEN=<same value as the service>
```

Then run the backend as usual (`uv run python manage.py migrate && uv run python manage.py runserver`).

**Try it:**

- `curl localhost:8001/health` should return `{"status": "ok", "active_run": null}`.
- http://localhost:8001/docs shows the interactive API docs.
- As a superuser, `POST /api/discovery/runs/ {"starting_point": "..."}` on the backend should reach `DONE`
  within a second or two, and the stub candidate should appear in `GET /api/discovery/candidates/`.
  Dismiss it afterwards.

**Notes:**

- Settings are read once, when the app is imported. Restart after changing `.env`.
- `fastapi dev` reloads on every code change, which cancels the active run (it's marked `FAILED`).

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `BACKEND_URL` | `http://localhost:8000` | Where the backend is. In Docker: `http://django:8000` |
| `DISCOVERY_SERVICE_TOKEN` | *(empty)* | Shared secret with the backend. **Empty means every `POST /runs` is refused** |
| `BACKEND_TIMEOUT_SECONDS` | `10` | Timeout for calls to the backend |
| `MISTRAL_API_KEY` | *(empty)* | Search and LLM calls |
| `MISTRAL_SMALL_MODEL` | `mistral-small-latest` | Classifying pages, picking links |
| `MISTRAL_LARGE_MODEL` | `mistral-medium-latest` | Interpreting the starting point, extraction |
| `MISTRAL_SEARCH_MODEL` | `mistral-medium-latest` | Model running the `web_search` tool |
| `LLM_TIMEOUT_SECONDS` | `60` | Timeout for LLM and search calls |
| `CACHE_DIR` | `./cache` | Page cache. A Docker volume in production |
| `CACHE_TTL_DAYS` | `30` | How long fetched pages are cached. `0` turns the cache off |
| `FETCH_TIMEOUT_SECONDS` | `15` | Timeout per page |
| `MAX_PAGE_BYTES` | `3000000` | Larger pages are truncated |
| `PER_DOMAIN_INTERVAL_SECONDS` | `1` | Minimum time between two requests to the same domain |
| `USER_AGENT` | `clapp-discovery/0.1 (…)` | Sent with every request. robots.txt rules for `clapp-discovery` apply |
| `MAX_LLM_CALLS` | `80` | Per-run limit |
| `MAX_PAGES` | `60` | Per-run limit |
| `MAX_SEARCHES` | `15` | Per-run limit |
| `MAX_LEADS` | `25` | Per-run limit: missing organisations researched |
| `MAX_HOPS_PER_SITE` | `3` | Per-run limit: links followed per site |
| `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT` | off | Optional LangSmith tracing |

Generate a token with `python -c "import secrets; print(secrets.token_urlsafe(32))"`.

## Tests

```bash
uv run pytest
```

The backend is never contacted. `tests/conftest.py`'s `FakeBackend` intercepts the `/internal/discovery/*`
calls with `respx`, records what the service sent (`updates`, `candidates`, `statuses`, `steps`) and
answers like the backend. Set `cancel_after_updates` to simulate a cancel. The app tests run the
real `lifespan` and call the app in-process through `httpx.ASGITransport`.

The tool tests never touch the network either: web pages are served by `respx` from
`tests/fixtures/`, the Mistral search client is replaced by a fake whose responses are parsed by the
SDK's own models (the SDK uses `httpx2`, which `respx` doesn't intercept), LLM calls use LangChain's
`GenericFakeChatModel`, and `tldextract` uses its bundled suffix list.

Lint and format with `uvx ruff check . && uvx ruff format .`.

## Reading a run

A run's state lives in the backend, in `DiscoveryRun` (Django admin → Discovery runs, or
`GET /api/discovery/runs/{id}/`):

- `status`: one of `QUEUED`, `RUNNING`, `DONE`, `FAILED` or `CANCELLED`
- `progress`: the list of `{at, step, message}` lines posted by the service
- `counters`: `searches`, `pages`, `llm_calls`, `leads`, `leads_missing` and `candidates`
- `error` / `errors`: why the run failed, and the problems it ran into along the way
- `last_heartbeat_at`: when the last PATCH arrived

The service's own logs (stdout) show when each run starts and finishes, and any tracebacks.
