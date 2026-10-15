# Plan: Discovering new festivals, residencies and venues

Scope: finding new organisations to apply to and getting them in front of the owner for review.
Drafting, sending and inbox handling are out of scope (see `LLM_AUTOMATION_PLAN.md` and `INBOX_PIPELINE_PLAN.md`).
This plan replaces step 4 of `LLM_AUTOMATION_PLAN.md`.

## Goal
- Regularly suggest organisations that aren't in the database yet.
- **Only the owner account runs discovery and reviews suggestions.** This mirrors how Brevo is limited to one account
  (`BREVO_PROFILE_EMAIL`, `profiles/emails.py:17`).
- **Accepted organisations are shared with every user:** existing users get a copy straight away, and new users get one at signup.
- Nothing is added without the owner's approval.
- Every suggestion shows how it was found (the path of pages and the text it was based on), so it can be checked quickly.
- Contact emails are never invented.

## Example workflow (the main use case)
1. Search: "juggler tour dates 2025".
2. A result is an **artist's personal website**.
3. Go to the artist's **calendar / tour dates** page.
4. Extract the list of festivals the artist performed at.
5. **Check clapp** for each one and keep only the missing ones.
6. For each missing festival: **find its official website**, go to its contact and application pages, and collect the details.
7. Create candidates for review.
8. The owner reviews them in clapp: accepting one creates a shared seed, dismissing removes it.
9. Done.

This is why discovery is built with **LangGraph**:
- The next step depends on what kind of page we land on (artist site, festival site, aggregator, irrelevant).
- Moving around a site ("find the calendar", "find the contact page") is a loop where the LLM picks links.
- Each missing festival becomes its own parallel sub-task (one per festival, using the `Send` API).
- Budgets and hop limits have to apply across the whole run.

Artist calendars are a good source: if a similar act played somewhere, that festival is probably a good fit.

## Current state (what we build on)
- **Seeds and per-user copies:**
  - Organisations with `user=NULL` are seeds. When a profile is created, `seed_user_organisations` (`profiles/signals.py`) copies every seed and its contacts to the new user, with `is_seed_clone=True`.
  - **Seeds added later never reach existing users**, and there is no link from a copy back to its seed.
  - Staff see seeds directly (`get_visibility_filter`, `organisations/views.py:75-78`). Everyone else sees only their own rows.
  - All organisations in the local database are seeds (363 festivals, 8 residencies, 188 venues), so the owner already works directly on seed rows.
  - Organisations created through the normal form are saved with `user=request.user` (`organisations/views.py:226-227`), so they are **not** shared.
  - The copy code includes `comments`, so whatever the owner writes in a seed's comments is copied to new users.
- **Web search:** `MistralClient.search()` uses a Mistral agent with the `web_search` tool (`services/mistral_service.py`).
  `extract_search_results()` (`organisations/llm.py`) **drops the citation URLs**, which discovery needs.
  `search()` is not counted by the rate limiter.
- **Structured extraction:** `MistralClient.parse()` with Pydantic models.
  `festivals/utils.py` and `residencies/utils.py` already contain good prompts for dates and application types.
- **Enrichment:** `GET /{entity}/{id}/enrich/` fills one organisation and the frontend shows a diff before saving.
- **Dedupe:** `normalize_domain()` (keeps subdomains). The Excel import dedupes per user by `name__iexact`, then by domain.
- **Scraper:** `apps/scraper` is a standalone FastAPI app with two parsers (Buskers Central and an "Open Street" listing).
  It writes nothing to the backend.
- **Targeting data:** `Performance.performance_type` and `genres`, `Profile.location`, `nationality`, `spoken_languages`.
- **Infrastructure:** Celery + Redis with beat in `clapp_backend/celery.py`. Postgres in prod, SQLite locally and in tests.
  LLM quota is 100 calls per user per day (`services/rate_limit.py`). There's no LangChain dependency yet.
- **UI pattern to copy:** the inbound-emails review queue (tabs plus approve/dismiss, `app/(main)/inbound-emails`).

## Design decisions

### 1. Discovery belongs to the owner only
- Add a setting `DISCOVERY_PROFILE_EMAIL`. It defaults to `BREVO_PROFILE_EMAIL`, and the check uses the same lowercased email comparison.
- Add a helper `is_discovery_owner(user)` and a DRF permission `IsDiscoveryOwner` on every discovery endpoint. Anyone else gets 403.
- The profile serializer exposes `can_use_discovery`, so the frontend only shows the Discover page and dashboard card to the owner.
- The owner must also be staff. That is how they see seed rows today, and it's already true for the owner account.
- Since there's a single reviewer, there are no per-user suggestions: one candidate table with one review state.

### 2. Accepting creates a seed, and the seed is copied to everyone
Accepting a suggestion:
1. Creates a **seed**: a Festival, Residency or Venue with `user=NULL` and `is_seed_clone=False`, plus its contacts.
   The owner sees it immediately through the staff visibility filter.
2. Queues `propagate_seed(model, seed_id)`, which copies the seed and its contacts to **every existing non-owner profile** (`is_seed_clone=True`).
   It skips a profile that already has a matching organisation (same domain, or same name and country), so nobody's own entry gets duplicated.
3. New users get the seed through the existing signup signal.

The copy code in `profiles/signals.py` is moved into a reusable function, `organisations/seeding.py: clone_seeds_for_profiles(seeds, profiles)`.
The signup signal and `propagate_seed` both call it.

Copies stay independent, as today. If the owner later edits or enriches the seed, existing copies don't change.

Text that is for the owner only (relevance reason, review notes) stays on the candidate. It is never written into the seed's `comments`, because those are copied to other users.

### 3. LangGraph for the workflow, with a thin LangChain layer
- **Dependencies:** `langgraph`, `langchain-core`, `langchain-mistralai`.
  Add `langgraph-checkpoint-postgres` only when resumable runs are needed (phase 5).
- **`services/llm/models.py: get_chat_model(purpose)`** returns `ChatMistralAI`. All structured outputs use `.with_structured_output(PydanticModel)`.
  The model can be changed in one place, e.g. a small model for link-picking and a larger one for extraction.
- **Budget callback:** a LangChain callback counts every LLM call against the run's budget and a separate `discovery` key in `services/rate_limit.py`.
  It stops the run cleanly when the budget is exceeded, so discovery never uses up the owner's 100-per-day interactive quota.
- **Search** stays on Mistral's `web_search` agent through `MistralClient`, wrapped behind a `SearchProvider` interface.
  It is changed to **return the citation URLs** (a new `extract_search_sources()`).
  I believe `ChatMistralAI` doesn't expose Mistral's built-in web search, so this stays outside LangChain; check before building.
  Brave or Tavily can be added later behind the same interface (LangChain has tools for both).
- **Tracing:** LangSmith, turned on with an environment setting (`LANGSMITH_TRACING`). Off in tests.
- **Review happens in the app, not inside the graph.** The graph ends by saving candidates.
  Reviews happen days later in the UI, so pausing graph runs with `interrupt()` and keeping them open would add state for no benefit.
- Moving `organisations/llm.py` (enrichment, email drafting) to LangChain is **not** part of this plan.

### 4. Code location
Create a `discovery/` Django app in the backend:
- `graph/state.py`, `graph/nodes/*.py`, `graph/build.py` for the graph
- `tools/fetch.py`, `tools/search.py`, `tools/links.py` for fetching, search and link handling
- `sources/` for the scraper parsers, ported from `apps/scraper/parser.py`, which can then be deleted

### 5. Facts must come from fetched pages
- The LLM extracts only from page text we fetched ourselves, never from the search agent's summary.
- After extraction, every email and URL is checked against the fetched text, and anything not found there is dropped.
- Link-following can only choose links that actually appear on the page: the LLM picks an index from a list, it doesn't write a URL.

## The graph

### State (`DiscoveryState`)
```
run_id
goal_queries          list[str]
frontier              list[PageTask{url, kind_hint, depth, found_via}]   pages still to visit
visited               set[url]
leads                 list[Lead{name, town, country, year, url?, found_via}]   orgs mentioned on artist/aggregator pages
missing_leads         list[Lead]       leads not yet in clapp
candidates            list[CandidateDraft]   (reducer: append)
budget                {llm_calls, pages, searches, max_*}
errors                list[str]
```

### Nodes and edges
```
START
  → plan_queries            settings + owner profile → ~10 queries (templates, optionally one LLM call to translate)
  → search                  SearchProvider → SearchHit list → frontier (+ peer-artist URLs from settings)
  → visit_page   ◄──────────────────────────┐   fetch one page from frontier (robots.txt, cache, per-domain delay)
  → classify_page                           │   LLM: ARTIST_SITE | ORG_SITE | AGGREGATOR | IRRELEVANT
      ├─ ARTIST_SITE → navigate("calendar / tour dates / past shows")
      │                 → extract_leads ────┤   list of {name, town, country, year, url?}
      ├─ AGGREGATOR  → extract_leads ───────┤
      ├─ ORG_SITE    → becomes a Lead with url
      └─ IRRELEVANT  → next page ───────────┘
  (when frontier is empty or the page budget is spent)
  → check_known             no LLM: dedupe leads against seeds, owner rows and existing candidates → missing_leads
  → fan out with Send(research_org, lead) for each missing lead, up to max_leads_per_run
        research_org (subgraph, one per lead):
          resolve_website     if there is no url: search "{name} {town} {year} festival", pick the official site
                              (LLM picks from hits, blocklisted hosts excluded)
          navigate("contact / application / open call / programme")   up to 2 extra pages on the same site
          extract_org         structured CandidateExtraction (reuses festivals/residencies prompt rules)
          verify              emails/URLs must appear in fetched text; require name + (website or email)
          → returns CandidateDraft (or a "not resolved" note)
  → dedupe_candidates       domain + eTLD+1 + fuzzy name/country across drafts and DB
  → score                   one batched LLM call against the owner profile; "a peer artist played here" is a strong signal
  → save                    DiscoveryCandidate rows + run counters
END
```

### `navigate(goal)`: a reusable subgraph for moving around a site
1. Take the links from the current page (anchor text + href), keep only same-domain links, and drop ones already visited.
   Rank them with keywords for the goal in several languages first (no LLM), e.g. agenda, dates, tour, calendrier, termine, contact, candidature, bewerbung, open call.
2. If there is no clear keyword match, the LLM picks one link **index** from the top 20, or "stop".
3. Fetch that link and check whether the goal is reached (a cheap LLM yes/no, or a keyword check).
4. Loop until the goal is reached or the hop limit is hit (`max_hops`, default 3). It returns the pages visited.

### Guardrails
- **Hard limits per run** (in `DiscoverySettings`, enforced in state and by the budget callback):
  - `max_pages` 60
  - `max_llm_calls` 80
  - `max_searches` 15
  - `max_leads_per_run` 25
  - `max_hops` 3
- LangGraph `recursion_limit` is set as a backstop.
- **Fetching:**
  - `httpx` + `trafilatura`, with a timeout and a size cap
  - respect `robots.txt`
  - at most 1 request per second per domain
  - cache by URL for 30 days, so re-runs are cheap
  - no Playwright for now: JS-only pages are logged as "empty content" and skipped
- **Blocklisted hosts** (social networks, ticketing sites, Wikipedia, news) can provide leads but are never an organisation's `website_url`.
  Artist calendars hosted on Facebook or Instagram are out of scope at first.
- Every node catches its own errors, adds them to `errors` and continues. One broken site must not stop the run.

## Data model (`discovery/models.py`)

```
DiscoveryCandidate
  org_type          FESTIVAL | RESIDENCY | VENUE
  name, country, town, description
  website_url, domain           (domain = normalize_domain(website_url), indexed)
  contact_emails    JSON list   (only verified emails)
  application_url, application_type
  dates / application dates     (same fields and formats as Festival / Residency)
  subtype           festival_type / venue_type
  genres            JSON list
  found_via         JSON list of {kind: SEARCH|ARTIST_SITE|AGGREGATOR|SEED_SOURCE, url, title}
                    e.g. "found on <artist>'s calendar (2025)"
  sources           JSON list of {url, title, snippet, fetched_at}   (pages the facts came from)
  relevance_score 0–1, relevance_reason
  state             PENDING | ACCEPTED | DISMISSED | ALREADY_KNOWN | UNRESOLVED | DEAD
  dismiss_reason    NOT_RELEVANT | WRONG_REGION | DEFUNCT | DUPLICATE | OTHER
  created_seed      generic FK to the seed Festival/Residency/Venue created on accept
  run               FK DiscoveryRun
  first_seen_at, last_checked_at
  llm_model, prompt_version

DiscoverySource                 (sites that produced leads, worth revisiting)
  url, domain, kind (ARTIST_SITE | AGGREGATOR)
  calendar_url      (where navigate() found the calendar)
  last_visited_at, leads_found, candidates_accepted
  enabled

DiscoveryRun
  trigger           SCHEDULED | MANUAL | SEED_SOURCE
  queries JSON, started_at, finished_at, status, error, errors JSON
  searches, pages_fetched, llm_calls, leads_found, leads_missing, candidates_created
  langsmith_trace_url (optional)

DiscoverySettings               (one row, edited by the owner)
  enabled, frequency (WEEKLY | MONTHLY)
  org_types         multi: FESTIVAL / RESIDENCY / VENUE
  countries         multi (empty = derived from the owner's location/nationality)
  peer_artist_urls  list (artists similar to the owner; their calendars are checked every run)
  extra_keywords    free text
  max_* limits      (see Guardrails)
```

Notes:
- Dismissed and unresolved candidates are kept, so the same organisation isn't researched again.
  `check_known` treats them as known, unless they're older than 12 months, in which case they're retried.
- `UNRESOLVED` means a lead whose official site couldn't be found. It's kept with its `found_via`, so the owner can still see it and look it up by hand.
- `DiscoverySource` lets the next run go straight back to productive artist calendars (via `calendar_url`) without searching.

## Review flow

**API** (`/api/discovery/`, all endpoints require `IsDiscoveryOwner`)
- `GET candidates/?state=PENDING`: candidate data, `found_via`, sources, score and reason.
- `POST candidates/{id}/accept/`
  - Takes optional field overrides, including correcting the org type.
  - Creates the seed plus contacts, runs `clean_organisation_data`, and queues `propagate_seed`.
  - Idempotent: a second accept returns the existing seed.
- `POST candidates/{id}/dismiss/` with a `reason`.
- `POST candidates/{id}/restore/`
- `POST runs/`: run now (manual trigger, one active run at a time).
- `GET runs/latest/`: status and counters for a "discovering…" indicator.
- `GET/PUT settings/`
- `GET/PATCH sources/`: see productive artist sites and turn them on or off.

**Frontend** (shown only when `profile.canUseDiscovery`)
- New `app/(main)/discover/page.tsx` that reuses the inbound-emails tab pattern: To review / Unresolved / Accepted / Dismissed.
- Each item card shows:
  - name, type, location, dates and application type
  - the relevance reason
  - **found via** (e.g. "Calendar of Artist X → festival site → contact page"), with source links and snippets you can expand
  - Accept (with an inline edit for type/name), and Dismiss with a reason menu
- A note on Accept: "This will be added for all users."
- A settings panel (org types, countries, peer artist URLs, frequency, limits) and a run status/"Run now" button at the top of the page.
- A dashboard card ("N new suggestions") and a sidebar entry, both owner-only.

## Feedback loop
- Dismiss reasons tune the next run:
  - Repeated `WRONG_REGION` dismissals lower the weight of that country.
  - `NOT_RELEVANT` reasons are passed to the scoring prompt as negative examples (the last 10).
  - `DEFUNCT` marks the candidate `DEAD`.
- `DiscoverySource.candidates_accepted` ranks artist sites: productive ones are revisited every run, and ones that produce nothing get turned off automatically after N runs.
- Accept and dismiss rates per query template are logged on `DiscoveryRun`.

## Scheduling and operations
- Celery beat `discovery.tasks.run_scheduled_discovery` runs daily. It does nothing unless `DiscoverySettings.enabled` is on and a run is due.
  The graph runs inside a single Celery task with a generous `time_limit`. The run's status is updated on `DiscoveryRun` as it goes.
- `discovery.tasks.refresh_candidates` runs monthly. It re-checks pending and unresolved candidates and enabled sources.
- Admin: list views for candidates, sources and runs, plus a "mark as duplicate" action.

## Phases

1. **Foundation**
   - `discovery` app, models, admin and migrations.
   - `DISCOVERY_PROFILE_EMAIL` and `IsDiscoveryOwner`.
   - Move the copy code into `organisations/seeding.py`. The signup signal uses it, and its existing tests must still pass.
   - `propagate_seed` task with its skip rule.
   - `services/llm/` (`get_chat_model`, budget callback), and `extract_search_sources`.
2. **Tools**
   - fetch (cache, robots.txt, politeness), link extraction and ranking
   - `SearchProvider`
   - `check_known` dedupe (domain, eTLD+1, fuzzy name)
   - port the scraper parsers as seed sources and delete `apps/scraper`
3. **Graph**
   - `navigate` subgraph, then `research_org` subgraph, then the main graph
   - Start with a single entry point, `run_discovery --start-url <artist site>`, to test the example workflow end to end.
   - Then add search-driven runs.
4. **API and UI:** candidates, sources, settings and runs API, Discover page, dashboard card, `can_use_discovery`.
5. **Automation and robustness**
   - Celery beat scheduling, feedback loop, `refresh_candidates`
   - Postgres checkpointer so a crashed run can resume, if runs turn out to be long
6. **Later:** a Brave or Tavily provider, Playwright fetching, Facebook/Instagram calendars.

## Testing
- **Access:** a non-owner gets 403 on every discovery endpoint, and `can_use_discovery` is false for them.
- **Seeding:**
  - accept creates a seed of the right type, with contacts
  - `propagate_seed` copies it to every non-owner profile, skips profiles that already have it, and doesn't create a copy for the owner
  - accept twice creates nothing new
  - a profile created afterwards gets the seed through the signup signal
- **Tools:**
  - link ranking and keywords in several languages
  - same-domain filtering
  - robots.txt and cache behaviour
  - email/URL verification against fixture text
  - dedupe (domain, eTLD+1, fuzzy name, `ALREADY_KNOWN` against seeds)
- **Nodes:** each node is tested on its own with LangChain's fake chat models (`GenericFakeChatModel` / a fake structured-output model) and fixture pages.
- **Graph end to end, with a "mini web" of fixture HTML served by `respx`:**
  - Pages: search results → artist homepage → calendar page (lists 4 festivals, 2 already in the DB) → festival homepages → contact pages.
  - Assert:
    - exactly 2 candidates are created, with verified emails and the correct `found_via` path
    - the known festivals are skipped
    - budget limits stop the run cleanly
    - one broken festival site produces an `UNRESOLVED` candidate without failing the run
- **Budget callback:** counting, stopping when the budget is exceeded, and not touching the interactive quota.

## Open questions
1. **Owner's manual adds:** organisations created through the normal form are currently private (`user=request.user`).
   Should the owner's manual adds also become seeds and be shared, like accepted suggestions?
2. **Backfill:** should a one-off `propagate_seed` run give existing users the seeds added after they signed up?
3. **Starting points:** are search queries plus a hand-picked list of peer artist URLs enough? Or should the graph also look for peer artists itself
   (e.g. "jugglers who performed at {known festival}"), which grows the source list automatically but costs more budget?
4. **Search provider:** stay with Mistral web search only, or add Brave/Tavily now (better control over results, and LangChain tools exist for both)?
5. **Venues:** include them from the start, or start with festivals and residencies?
6. **Accept behaviour:** run enrichment automatically before creating the seed, or leave it to the enrich button?
