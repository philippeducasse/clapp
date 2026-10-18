# clapp discovery service

Finds new festivals, residencies and venues from a **starting point** (a link, a request in plain
words, or both) and proposes them to superusers for review in clapp.

This service runs in its own container and has **no database**. Everything it finds is stored by
the backend's `discovery` Django app (`apps/backend/discovery`), which also handles the review
(accept / dismiss) and turns accepted candidates into seeds shared with every user.

See `DISCOVERY_PLAN.md` at the repo root for the full plan.

> **Status:** the plan is implemented. The service runs the LangGraph workflow
> (`discovery/graph/`), superusers use it from the **Discover** page (`/discover`), and it deploys
> as its own container (see [Deployment](#deployment)). Set `USE_STUB_GRAPH=true` to run the stub
> graph instead: it posts a few progress lines and one fake candidate ("Stub festival (run N)")
> without any LLM or web calls.

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
  prompts/           one module per LLM call: output schema + messages()
    interpret.py     plain-words request → goal, org types, countries, search queries
    classify.py      ARTIST_SITE | ORG_SITE | AGGREGATOR | IRRELEVANT
    pick_link.py     link numbers to follow (navigate's fallback)
    pick_website.py  number of the official site among search results
    extract_leads.py organisations named on a calendar or listing page
    extract_org.py   the candidate's facts (date / application rules copied from the backend)
  graph/
    build.py         the main graph, run_discovery(), discovery_graph (what the app runs)
    state.py         DiscoveryState, PageTask, Lead, add_hop
    deps.py          Deps (tools + run-wide bookkeeping, the LangGraph runtime context), guarded
    navigate.py      navigate(goal): keyword ranking, then LLM picks link numbers
    leads.py         same organisation?, country filter, merging leads and candidates
    research_org.py  the per-lead subgraph and build_candidate (verification)
    nodes/           explore.py, check_known.py, finish.py
tests/
  conftest.py        settings fixture, FakeBackend (respx mock of /internal/discovery/*), fixture loaders
  fixtures/          saved HTML pages (artist home, calendar, festival contact, JavaScript-only page)
  test_app.py        HTTP endpoints: token, 202/409/422, shutdown
  test_runner.py     run lifecycle: DONE / CANCELLED / FAILED, backend client errors
  test_llm.py, test_search.py, test_fetch.py, test_links.py, test_known.py, test_verify.py
  graph_fakes.py     ScriptedChatModel, FakeSearch, FakeWeb (respx)
  test_graph_nodes.py  each node on its own
  test_graph_e2e.py  the whole graph on a small fake web (tests/fixtures/web/)
```

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

## The graph (step 5)

```
START
 → interpret_start   URL(s) → pages to visit; plain words → LLM {goal, org_types, countries,
                     queries}; both → both, and the request text becomes the goal
 → load_known        GET known-index/
 → search            (only if there are queries) result pages join the pages to visit
 → visit_page ◄────────────────────────────────────────────┐
 → classify_page     ARTIST_SITE  → find_calendar → extract_leads ┤
                     AGGREGATOR   → extract_leads ─────────────────┤
                     ORG_SITE     → add_org_lead ──────────────────┤
                     IRRELEVANT   ─────────────────────────────────┘
   (until no pages are left or exploring has used its share of the budget)
 → check_known       drop leads clapp already has; keep up to MAX_LEADS missing ones
 → research_org × each missing lead, in parallel (Send; RESEARCH_CONCURRENCY at a time)
      resolve_website  no URL? search "{name} {town} {year}", LLM picks a result by number;
                       a site clapp already has ends the research
      visit_site       the site + navigate("contact", "application"), up to 2 more pages
      extract_org      structured facts
      verify           build_candidate: keep only what the fetched pages show
 → dedupe_candidates  merge duplicates; drop any clapp has under the researched name/site
 → save               POST candidates (one by one if the batch is refused) and sources
END
```

**Rules every node follows**

- It posts a short progress line, which is also the heartbeat. A reply with `cancel_requested`
  raises `RunCancelled`, which goes straight through the graph: the run ends `CANCELLED` and
  nothing is saved.
- It catches its own errors (`guarded` in `graph/deps.py`): they're posted to the run's `errors`
  and the node carries on with what it has, so one broken site doesn't stop the run. Backend
  errors are the exception: without the backend nothing can be saved, so the run fails.
- `BudgetExceeded` stops the part of the work that hit it. The candidates found so far are still
  saved and the run ends `DONE` with "budget reached: …" in the final line.

**Budget**

- Exploring (visiting pages, classifying, reading calendars) may use `EXPLORE_SHARE` (half) of the
  page and LLM-call budgets, so researching the leads always has something left.
- A page is fetched, and counted, once per run (`Deps.fetch` remembers pages and failures).
- `navigate` follows at most `MAX_HOPS_PER_SITE` links per site over the whole run.
- `recursion_limit` (`MAX_PAGES × 5 + 30` steps) is a safety net against loops.

**What the LLM is never trusted with**

- URLs: links are always picked **by number** from a list the workflow built (`navigate`,
  `extract_leads`, `resolve_website`). An extracted `application_url` is kept only if it appears
  on the organisation's pages.
- Emails: kept only if they appear on the pages fetched for that organisation. With no extracted
  contacts, up to 3 emails of the site's own domain found on those pages are used instead.
- Choices: `subtype` and `application_type` must be one of the backend's choices for that type;
  dates must be ISO. Anything else is dropped.
- Web content is wrapped in `<page>` tags and the prompts say it's data, not instructions.

**PENDING or UNRESOLVED.** A candidate needs a name and either a website that could be read or a
verified email. Otherwise it's saved as `UNRESOLVED`, and `relevance_reason` starts with "Could
not research: …" (no website found, site unreachable, JavaScript-only…). A lead skipped because
the budget ran out before anything was fetched is **not** saved (the known-index includes every
candidate, so it would never be proposed again); its name appears in the progress log.

**found_via and sources.** `found_via` is the path to the organisation, one hop per page:
`start` / `search` → `artist_site` | `aggregator` → `calendar` → `festival_site` (or
`residency_site`, `venue_site`, `org_site`) → `contact` / `application`. A hop to the same page as
the previous one replaces it, so a search result that turns out to be an artist site is one hop
(`artist_site`, with the query in `snippet`). `sources` lists the pages the facts came from: the
listing page and the organisation's pages, with the first 300 characters of each.

**Counters** posted with every progress line: `pages`, `searches`, `llm_calls` (spent),
`leads` (found while exploring), `leads_missing` (not in clapp), `candidates` (saved).

**Defaults.** A starting point with only links looks for festivals (`org_types: ["FESTIVAL"]`).
A plain-words request gets up to 5 search queries (`min(5, MAX_SEARCHES / 2)`); the rest of the
search budget is for finding websites of leads.

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
- With `USE_STUB_GRAPH=true`: as a superuser, `POST /api/discovery/runs/ {"starting_point": "..."}`
  on the backend should reach `DONE` within a second or two, and the stub candidate should appear
  in `GET /api/discovery/candidates/`. Dismiss it afterwards.
- With the real graph (needs `MISTRAL_API_KEY`): start a run from an artist's website and follow
  `GET /api/discovery/runs/{id}/`'s `progress`. Lower `MAX_PAGES` / `MAX_LLM_CALLS` while trying
  things out.

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
| `EXPLORE_SHARE` | `0.5` | Share of the page and LLM-call budgets exploring may use; the rest is for research |
| `RESEARCH_CONCURRENCY` | `4` | Leads researched at the same time |
| `USE_STUB_GRAPH` | `false` | Run the stub graph (one fake candidate, no LLM or web calls) |
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

The graph tests (`test_graph_nodes.py`, `test_graph_e2e.py`) use `tests/graph_fakes.py`:
`ScriptedChatModel` is a LangChain chat model whose answers come from a Python function of
(purpose, prompt), and goes through LangChain's callbacks so the budget counts it; `FakeSearch`
answers from a dict; `FakeWeb` serves `tests/fixtures/web/` with `respx` (anything else is a 404).
The end-to-end test runs an artist site → a calendar with 4 festivals, 2 already known → the 2
festival sites and their contact pages, and checks the posted candidates, `found_via` paths,
verified emails, sources and counters; other cases cover a broken site, the page and LLM budgets,
a cancel, a plain-words request, and a batch the backend refuses.

The tool tests never touch the network either: web pages are served by `respx` from
`tests/fixtures/`, the Mistral search client is replaced by a fake whose responses are parsed by the
SDK's own models (the SDK uses `httpx2`, which `respx` doesn't intercept), LLM calls use LangChain's
`GenericFakeChatModel`, and `tldextract` uses its bundled suffix list.

Lint and format with `uvx ruff check . && uvx ruff format .`.

## Using it (frontend)

Superusers see **Discover** in the sidebar (everyone else doesn't, and the API answers 403).

1. Type a starting point: a link, a request in plain words, or both, and press **Discover**. The
   button is disabled while a run is active (one run at a time).
2. The run panel polls the run every 3 seconds: status, the progress log, the counters and a
   **Cancel** button. The dropdown above it shows recent runs.
3. Candidates appear in **To review** (or **Unresolved**) when the run finishes. Each card shows the
   facts, the **found via** path (each hop links to the page), the sources and the relevance reason.
   - **Accept** creates a seed and copies it to every user. **Edit name and type** first if needed.
   - **Dismiss** with a reason; dismissed candidates can be moved back to review.

Frontend code: `app/(main)/discover/page.tsx`, `components/page-components/discover/`,
`api/discoveryApiService.ts`, `interfaces/entities/Discovery.ts`, and `sidebarItems.ts`.

## Deployment

- **Image:** `apps/discovery/dockerfile` (multi-stage uv build, non-root user, runs
  `uvicorn discovery.app:app --host 0.0.0.0 --port 8001`, healthcheck on `/health`).
- **Compose:** the `discovery` service in `apps/backend/docker/docker-compose.yml`. It has no
  published ports and no nginx route, so only `clapp-network` can reach it. The page cache is the
  `discovery_cache` volume (`/app/cache`). `BACKEND_URL=http://django:8000` is set in the compose
  file.
- **Environment:** the service reads `~/clapp/.env.discovery` (`DISCOVERY_SERVICE_TOKEN`,
  `MISTRAL_API_KEY`). It's a separate file because `backend-deploy.yml` overwrites `~/clapp/.env`
  on every deploy. The file is optional for compose: without it the service starts but refuses
  every run. The backend's `.env` gets `DISCOVERY_SERVICE_URL=http://discovery:8001` and
  `DISCOVERY_SERVICE_TOKEN` from `backend-deploy.yml`.
- **GitHub secrets:** `DISCOVERY_SERVICE_TOKEN` (required, same value on both sides) and
  `DISCOVERY_MISTRAL_API_KEY` (optional; without it the backend's `MISTRAL_API_KEY` is used, so
  set it if you want discovery's usage tracked separately).
- **Workflows:**
  - `discovery-tests.yml`: on pushes and PRs touching `apps/discovery/**`, runs ruff and pytest.
  - `discovery-deploy.yml`: on pushes to `production` touching `apps/discovery/**`, runs the
    tests, builds and pushes `clapp_discovery`, writes `.env.discovery` and copies it and the
    compose file to the server, then `docker compose pull discovery && docker compose up -d
    discovery`.
- **First rollout:**
  1. Add the GitHub secrets.
  2. Push the `apps/discovery` change to `production` first, so the `clapp_discovery` image exists.
  3. Then deploy the backend change that adds `discovery` to the compose file. Otherwise the
     backend deploy's `docker compose pull` fails on the missing image.
- **Kill switch:** `docker compose stop discovery`. The backend then marks new runs FAILED
  ("discovery service unreachable"), and the rest of clapp is unaffected.

Build and try the image locally:

```bash
docker build -f apps/discovery/dockerfile -t clapp_discovery:local apps/discovery
docker run --rm -p 8001:8001 -e DISCOVERY_SERVICE_TOKEN=change-me clapp_discovery:local
curl localhost:8001/health
```

## Reading a run

A run's state lives in the backend, in `DiscoveryRun` (Django admin → Discovery runs, or
`GET /api/discovery/runs/{id}/`):

- `status`: one of `QUEUED`, `RUNNING`, `DONE`, `FAILED` or `CANCELLED`
- `progress`: the list of `{at, step, message}` lines posted by the service
- `counters`: `searches`, `pages`, `llm_calls`, `leads`, `leads_missing` and `candidates`
- `error` / `errors`: why the run failed, and the problems it ran into along the way
- `last_heartbeat_at`: when the last PATCH arrived

The service's own logs (stdout) show when each run starts and finishes, and any tracebacks.
