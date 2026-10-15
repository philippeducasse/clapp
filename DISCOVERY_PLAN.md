# Plan: Discover (finding new festivals, residencies and venues)

Scope: a superuser-only tool that starts from a **starting point** (a link, a request in plain words, or both),
explores the web, and proposes new organisations for review. Accepted organisations become seeds shared with every user.
Drafting, sending and inbox handling are out of scope (see `LLM_AUTOMATION_PLAN.md` and `INBOX_PIPELINE_PLAN.md`).
This plan replaces step 4 of `LLM_AUTOMATION_PLAN.md`.

## What it does

- Superusers get a **Discover** entry in the sidebar. Other users see nothing, and the API returns 403 for them.
- The Discover page has a **starting point** text box that accepts anything:
  - `https://some-juggler.com`
  - `street theatre festivals in Belgium with open calls for 2027`
  - `check the tour dates on https://some-juggler.com and find festivals we don't have`
- A LangGraph workflow explores from there. The main example:
  1. Land on an artist's website.
  2. Find the calendar / tour dates page.
  3. List the festivals the artist played at.
  4. Check which ones clapp already has.
  5. Research each missing festival: use the entich() function (in apps/backend/organisations/views.py)
  6. Save them as **candidates**.
- The superuser reviews the candidates on the same page.
  - **Accept** creates a seed (`user=NULL`) and copies it to every user: existing users get it straight away, new users at signup.
  - **Dismiss** removes it from the list.
- Nothing is added to clapp without approval. Every candidate shows how it was found and which pages its facts came from.
  Contact emails are never invented.

## Architecture

The discovery code (LangGraph, scraping, AI libraries) lives in a **separate service**, `apps/discovery`,
so none of it ships in the main backend image. The backend only gets a thin `discovery` Django app
(models, review API and accept), with no new dependencies.

```
browser ──► frontend (/discover, superusers only)
               │  /api/discovery/*   (session auth, superuser only)
               ▼
            backend (Django)  ── stores runs, candidates, sources; review; accept → seed → propagate
               │  ▲
   start run   │  │  /internal/discovery/*   (service token)
   (HTTP)      ▼  │  progress, known-index, candidates, cancel check
            apps/discovery (FastAPI + LangGraph, own container, no database)
               │
               ▼
            web (search, artist sites, festival sites)
```

**Why it's split this way:**

- **Backend:** data that belongs to clapp (candidates, seeds, copies to users) stays where the models are.
  The frontend only talks to the backend, so there's no CORS or extra login to set up.
- **Service:** all the heavy and risky parts: LangGraph, LangChain, fetching pages, the cache, and later Playwright.
  It can be deployed, restarted or turned off without touching the main app.
- **Service-facing endpoints** live under `/internal/discovery/`, not `/api/`.
  - In prod, nginx only sends `/clappmin/` and `/health/` to Django, and Next.js only rewrites `/api/*` (`next.config.ts`).
    So `/internal/` can't be reached from outside; only the `discovery` container can call it over `clapp-network`.
  - It also requires `Authorization: Bearer <DISCOVERY_SERVICE_TOKEN>`.

## Current state (what we build on)

- **Seeds and per-user copies:**
  - Organisations with `user=NULL` are seeds. `seed_user_organisations` (`profiles/signals.py`) copies every seed and its contacts to each **new** user, with `is_seed_clone=True`.
  - Seeds added later never reach existing users.
  - Staff see seeds directly (`get_visibility_filter`, `organisations/views.py:75-78`). Superusers are staff by default (`profiles/models.py:49-50`).
  - All organisations in the local database are seeds (363 festivals, 8 residencies, 188 venues).
  - The copy code includes `comments`, so whatever is written in a seed's comments is copied to new users.
- **Profile API:** `ProfileSerializer` doesn't expose `is_superuser`, so the frontend can't tell who is a superuser yet.
- **Sidebar:** `Sidebar.tsx` uses a fixed list of items, and `index == 6` pushes "Report a bug" and the items after it to the bottom.
- **Web search:** `MistralClient.search()` uses a Mistral agent with `web_search` (`services/mistral_service.py`).
  `extract_search_results()` (`organisations/llm.py`) drops the citation URLs. The service will have its own search client that keeps them.
- **Prompts worth reusing:** the date and application-type rules in `organisations/festivals/utils.py` and `organisations/residencies/utils.py`.
- **Dedupe helper:** `normalize_domain()` in `organisations/utils.py` (keeps subdomains).
- **Deployment:**
  - `apps/backend/docker/docker-compose.yml` runs `db`, `django`, `next`, `nginx`, `redis`, `celery_worker` and `celery_beat` on `clapp-network`.
  - `backend-deploy.yml` overwrites `~/clapp/.env` on every deploy and copies the compose file and `nginx.conf` when they change.
- **UI pattern to copy:** the inbound-emails review queue (`app/(main)/inbound-emails`, tabs plus approve/dismiss).
- `apps/scraper` is left as it is.

## Steps

### Step 1: Backend, superuser flag and sharing seeds with every user

1. `ProfileSerializer`: add `is_superuser` (read-only). On the frontend, add `isSuperuser?: boolean` to `Profile.ts`.
2. Move the copy code from `profiles/signals.py` into `organisations/seeding.py`:
   - `clone_seeds_for_profiles(seeds, profiles)` copies organisations and their contacts.
   - The signup signal calls it with all seeds and the one new profile, so its behaviour doesn't change.
3. Celery task `organisations.tasks.propagate_seed(model_label, seed_id)` copies a single seed to every existing **non-superuser** profile.
   It skips a profile that already has a matching organisation: same `normalize_domain(website_url)`, or same name (case-insensitive) and country.
4. Tests:
   - the serializer returns `is_superuser`
   - the signup signal still copies everything (the existing tests pass unchanged)
   - `propagate_seed` copies to the right profiles, skips duplicates, never copies to superusers, and running it twice creates nothing new

### Step 2: Backend, the `discovery` Django app (thin, no new dependencies)

**Models**

```
DiscoveryRun
  starting_point      text (raw input)
  status              QUEUED | RUNNING | DONE | FAILED | CANCELLED
  cancel_requested    bool
  plan                JSON   (how the service interpreted the starting point)
  progress            JSON list of {at, step, message}   (shown live on the page)
  counters            JSON   {searches, pages, llm_calls, leads, leads_missing, candidates}
  errors              JSON list
  created_by          FK Profile
  created_at, started_at, finished_at, last_heartbeat_at

DiscoveryCandidate
  run                 FK DiscoveryRun
  org_type            FESTIVAL | RESIDENCY | VENUE
  name, country, town, description
  website_url, domain (normalize_domain, indexed)
  contact_emails      JSON list (only verified emails)
  contacts            JSON list of {name, email, role}
  application_url, application_type
  start_date, end_date, approximate_date, application_date_start, application_date_end   (same formats as Festival)
  subtype             festival_type / venue_type
  found_via           JSON list of {kind, url, title}   e.g. search → artist site → calendar → festival site
  sources             JSON list of {url, title, snippet}  (pages the facts came from)
  relevance_reason    short text
  state               PENDING | ACCEPTED | DISMISSED | ALREADY_KNOWN | UNRESOLVED
  dismiss_reason      NOT_RELEVANT | WRONG_REGION | DEFUNCT | DUPLICATE | OTHER
  created_seed        generic FK (Festival / Residency / Venue)
  created_at

DiscoverySource       (artist and aggregator sites that produced leads, for reuse)
  url, domain, kind (ARTIST_SITE | AGGREGATOR), calendar_url
  last_visited_at, leads_found, candidates_accepted
```

Plus admin pages for all three.

**Settings:** `DISCOVERY_SERVICE_URL` (default `http://discovery:8001`) and `DISCOVERY_SERVICE_TOKEN`.

**Frontend-facing API: `/api/discovery/`** (session auth, `IsSuperuser` permission)

- `POST runs/ {starting_point}`
  - Creates a QUEUED run, then calls the service at `POST {DISCOVERY_SERVICE_URL}/runs` with `{run_id, starting_point}` (5-second timeout).
  - If the service can't be reached, the run is marked FAILED with "discovery service unreachable".
  - Only one active run at a time; a second request gets 409.
- `GET runs/` lists recent runs.
- `GET runs/{id}/` returns status, progress and counters, polled by the page.
  - A RUNNING run with no heartbeat for 10 minutes is marked FAILED when it's read, which covers a service restart in the middle of a run.
- `POST runs/{id}/cancel/` sets `cancel_requested`.
- `GET candidates/?state=&run=`
- `POST candidates/{id}/accept/ {overrides?}`
  - Creates the seed (`user=NULL`, `is_seed_clone=False`) and its contacts, runs `clean_organisation_data`, and queues `propagate_seed`.
  - Accepting twice returns the existing seed.
  - `relevance_reason` is **not** copied into the seed's `comments`, because those are copied to other users.
- `POST candidates/{id}/dismiss/ {reason}` and `POST candidates/{id}/restore/`

**Service-facing API: `/internal/discovery/`** (service token, not reachable from outside)

- `PATCH runs/{id}/` sets status, adds progress lines, counters, errors and the plan, and updates `last_heartbeat_at`.
  The response includes `cancel_requested`, so the service learns about a cancel on every progress update.
- `GET known-index/` returns `[{name, country, town, domain, org_type, source: SEED|SUPERUSER|CANDIDATE}]` for:
  - all seeds
  - organisations owned by superusers
  - all existing candidates, whatever their state

  It's about 600 short rows; the service fetches it once per run and does the fuzzy matching itself.

- `POST runs/{id}/candidates/` takes a list of candidates and saves them.
  The backend runs its own exact check (domain, or name + country) and saves matches as `ALREADY_KNOWN`, as a safety net.
- `POST sources/` upserts `DiscoverySource` rows.

**Tests:**

- permissions: 403 for non-superusers, 401 for a missing or wrong service token
- the one-run-at-a-time rule
- the service being unreachable marks the run FAILED
- the heartbeat timeout
- accept, dismiss and restore
- the `known-index` contents
- the `ALREADY_KNOWN` safety net

The service call is mocked with `respx` or by patching `httpx`.

### Step 3: Service skeleton (`apps/discovery`)

```
apps/discovery/
  pyproject.toml          uv; fastapi, uvicorn, httpx, pydantic-settings,
                          langgraph, langchain-core, langchain-mistralai, mistralai,
                          trafilatura, tldextract, rapidfuzz, diskcache
  dockerfile
  .env.example
  discovery/
    app.py                FastAPI: GET /health, POST /runs
    config.py             BACKEND_URL, DISCOVERY_SERVICE_TOKEN, MISTRAL_API_KEY, limits, LANGSMITH_*
    backend_client.py     typed calls to /internal/discovery/*
    runner.py             runs one graph in the background; one run at a time (409 otherwise)
    llm.py                get_chat_model(purpose) → ChatMistralAI; RunBudget callback
    prompts/              classify, extract_leads, extract_org (date/application rules copied from the backend), pick_link
    tools/                fetch.py, links.py, search.py, known.py, verify.py
    graph/                state.py, nodes/*.py, navigate.py, research_org.py, build.py
  tests/
    fixtures/             saved HTML pages for a small fake web
```

1. `POST /runs {run_id, starting_point}` checks the token and returns 202 straight away. The graph then runs as a background asyncio task.
2. `runner.py` runs a **stub graph** first: it posts a few progress lines and one fake candidate, then sets the run to DONE.
   That proves the backend ↔ service ↔ frontend loop works before any LLM code exists.
3. Local development:
   - Run the service with `uv run fastapi dev discovery/app.py --port 8001`.
   - The backend gets `DISCOVERY_SERVICE_URL=http://localhost:8001`, and the service gets `BACKEND_URL=http://localhost:8000`.
   - Both use the same token.

### Step 4: Service tools

1. **`llm.py`**
   - `get_chat_model(purpose)`: a small model for classifying pages and picking links, a larger one for extraction. All use `.with_structured_output()`.
   - The `RunBudget` LangChain callback counts LLM calls and raises `BudgetExceeded` at the limit.
   - **Default limits per run:** 80 LLM calls, 60 pages, 15 searches, 25 leads researched, 3 link hops per site.
   - LangSmith tracing can be turned on with an environment variable.
2. **`tools/search.py`:** Mistral `web_search` agent (same approach as the backend's `MistralClient`). It returns `list[SearchHit{url, title, snippet}]`, **including the citation URLs**.
   It sits behind a `SearchProvider` interface, so Brave or Tavily can be added later.
3. **`tools/fetch.py`:**
   - `httpx` + `trafilatura`, with a timeout and a page-size cap
   - respects `robots.txt`
   - at most 1 request per second per domain
   - pages cached for 30 days in `diskcache`, on a Docker volume
   - JavaScript-only pages are logged as "empty content" and skipped
4. **`tools/links.py`:** extracts same-domain links (anchor text + URL) and ranks them using keywords in several languages
   (agenda, dates, tour, calendrier, termine, contact, candidature, bewerbung, open call, appel).
5. **`tools/known.py`:** loads the `known-index` and checks leads against it by:
   - domain
   - registrable domain (`tldextract`)
   - a `rapidfuzz` name match ≥ 90 within the same country
6. **`tools/verify.py`:** keeps an email or URL only if it appears in text the workflow fetched itself.
   Blocklisted hosts (social networks, ticketing sites, Wikipedia, news) are never used as an organisation's `website_url`.
7. Unit tests for each tool.

### Step 5: The graph

```
START
 → interpret_start   URL(s) in the text      → pages to visit
                     plain-words request     → LLM returns {goal, org_types, countries, queries}
                     both                    → both; the request text becomes the goal
 → load_known        GET /internal/discovery/known-index/
 → search            (only if there are queries) → add the result links to the pages to visit
 → visit_page ◄──────────────────────────────┐
 → classify_page     ARTIST_SITE | ORG_SITE | AGGREGATOR | IRRELEVANT   (judged against the goal)
     ARTIST_SITE → navigate("calendar / tour dates") → extract_leads ─┤
     AGGREGATOR  → extract_leads ──────────────────────────────────────┤
     ORG_SITE    → becomes a lead with its URL                        │
     IRRELEVANT  → next page ──────────────────────────────────────────┘
   (stops when there are no pages left or the page budget is used up)
 → check_known       drop leads clapp already has → the missing leads
 → Send(research_org, lead) for each missing lead (up to 25), in parallel
      research_org:
        resolve_website   no URL? search "{name} {town} {year}" and the LLM picks the official site from the results
        navigate("contact / application / open call")   up to 2 more pages
        extract_org       structured candidate (dates and application type, using the copied prompt rules)
        verify            check emails/URLs; needs a name + (website or email); otherwise the lead is UNRESOLVED
 → dedupe_candidates  among this run's candidates
 → save               POST candidates and sources to the backend; status DONE
END
```

- `navigate(goal)` is a reusable subgraph. It tries keyword ranking first. If that doesn't find a clear match, the LLM picks the **number** of a link from the top 20, or "stop".
  It never writes a URL itself. At most 3 links per site.
- Every node:
  - posts a short progress line, which also counts as the heartbeat
  - stops the run cleanly if `cancel_requested` comes back as true
  - catches its own errors, so one broken site doesn't stop the run
- If the budget runs out, the candidates found so far are still saved and the run is marked DONE with a "budget reached" note.
- `recursion_limit` is a safety net in case the workflow keeps looping.
- **Tests:**
  - Each node on its own, using LangChain's fake chat models and saved HTML pages.
  - **End to end on a small fake web served by `respx`:** artist site → calendar listing 4 festivals, 2 of them in the fake known-index → festival sites → contact pages. It should:
    - post exactly 2 candidates, with verified emails and the right `found_via` paths
    - skip the 2 known festivals
    - produce an `UNRESOLVED` candidate for a broken site, without failing the run
    - stop cleanly when the budget runs out or a cancel is requested

### Step 6: Frontend

1. **`Sidebar.tsx`:**
   - Add `{ title: "Discover", url: "/discover", icon: Compass, superuserOnly: true }` after "Inbound emails".
   - Filter the list using `profile.isSuperuser` from Redux.
   - Replace the `index == 6` check with a `bottom: true` flag on "Report a bug".
2. **`app/(main)/discover/page.tsx`** (redirects to `/dashboard` if the user isn't a superuser):
   - **Starting point bar:** one text field with the placeholder "Paste a link, describe what to look for, or both…", plus a **Discover** button.
     The button is disabled while a run is active.
   - **Run panel:** status, the live progress log (polled every 3 seconds while the run is active), counters and a Cancel button.
     Below it, a dropdown of recent runs.
   - **Candidates:** tabs for To review / Unresolved / Accepted / Dismissed, using the inbound-emails pattern. Each card shows:
     - name, type, location, dates and application type
     - **found via**, e.g. "Calendar of X → festival site → contact page", with source links
     - the relevance reason
     - **Accept**, with inline editing of type and name, and the note "This will be added for all users"
     - **Dismiss**, with a menu of reasons
3. `api/discoveryApiService.ts` and `interfaces/entities/Discovery.ts`.
4. After an accept, refresh the matching Redux slice (festivals, venues or residencies).
5. Tests for the API service and the sidebar filtering.

### Step 7: Deployment

1. **`apps/discovery/dockerfile`:** multi-stage uv build, the same pattern as the backend's. It runs `uvicorn discovery.app:app --port 8001`.
2. **`docker-compose.yml`:** add the new service.
   ```
   discovery:
     restart: unless-stopped
     image: ${REGISTRY_URL}/clapp_discovery:latest
     env_file: [.env.discovery]
     volumes: [discovery_cache:/app/cache]
     networks: [clapp-network]
     healthcheck: GET http://localhost:8001/health
   ```

   - No published ports and no nginx route.
   - Add `discovery_cache` to the volumes.
3. **Environment:**
   - The service uses a **separate** `~/clapp/.env.discovery`, because `backend-deploy.yml` overwrites `~/clapp/.env` on every deploy.
   - Add `DISCOVERY_SERVICE_URL` and `DISCOVERY_SERVICE_TOKEN` to the backend's `.env` section in `backend-deploy.yml`.
   - Add GitHub secrets for `DISCOVERY_SERVICE_TOKEN` and, if you want a separate key, a Mistral key for discovery.
4. **Workflows:**
   - `discovery-tests.yml`: runs on `apps/discovery/**`, `uv sync` + `pytest`.
   - `discovery-deploy.yml`: runs on pushes to `production` that touch `apps/discovery/**`. It:
     - runs the tests
     - builds and pushes `clapp_discovery`
     - writes `.env.discovery` on the server
     - runs `docker compose pull discovery && docker compose up -d discovery`
5. **Rollout order:**
   1. Push the `clapp_discovery` image first.
   2. Then deploy the backend change that adds `discovery` to the compose file. Otherwise the backend deploy's `docker compose pull` fails on a missing image.
6. **Kill switch:** `docker compose stop discovery`. The backend then marks new runs FAILED ("service unreachable"), and the rest of clapp is unaffected.

### Step 8: Docs and clean-up

- `apps/discovery/README.md`: how to run it locally, environment variables, limits, and how to read a run.
- Replace step 4 of `LLM_AUTOMATION_PLAN.md` with a link to this plan.

## Not in this version

- Scheduled or automatic runs: every run starts from the starting point bar.
- Playwright for JavaScript-heavy sites, and Facebook or Instagram calendars.
- Brave or Tavily search.
- Saving graph state so a crashed run can resume: for now a crashed run is marked FAILED and you start it again.
- Learning from dismissals, relevance scores, and revisiting productive `DiscoverySource` sites automatically.
- Automatically enriching a candidate when it's accepted (the existing enrich button still works on the seed).

## Open questions

1. **Manual adds by superusers:** organisations created through the normal form are private (`user=request.user`). Should they also become shared seeds?
2. **Backfill:** should a one-off `propagate_seed` run give existing users the seeds that were added after they signed up?
3. **Venues:** include them from the start, or start with festivals and residencies?
4. **Mistral key:** should discovery share the backend's Mistral key, or have its own so its usage and cost are tracked separately?
