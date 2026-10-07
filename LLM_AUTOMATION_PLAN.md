# Plan: LLM automations (drafting → approval → sending, inbox replies, discovery)

## Goal
- Regularly prepare application drafts automatically.
- Send them only after manual approval.
- Detect responses in the inbox (see `INBOX_PIPELINE_PLAN.md`).
- Discover new festivals and venues to apply to.
- Use LangChain/LangGraph where it adds value.

## Existing building blocks
- **Drafting:** `organisations/llm.py` (Mistral, including web search for enrichment).
- **Sending:** `organisations/emails.py` (`prepare_application_email`, `send_application_email`, Brevo).
- **Inbox:** `applications/inbox.py` and the `InboundEmail` model. `check_inbox_task` runs on Celery beat every 10 min.
- **Scraper:** `apps/scraper` (small standalone script: `main.py`, `parser.py`).
- **Infrastructure:** Celery + Redis, Pydantic, Mistral SDK, and `normalize_domain` in `organisations/utils.py`.

`INBOX_PIPELINE_PLAN.md` decided against LangChain for inbox classification, since it's a single structured call per email.
LangChain is used mainly for multi-step work: discovery, and drafting.

## Steps

### 1. LangChain foundation (`services/llm/`)
- Add dependencies: `langchain`, `langchain-mistralai`, `langgraph` (plus `langchain-community` if loaders or tools are needed).
- `get_chat_model()` factory around `ChatMistralAI`, so the provider can be changed in one place.
- Use `.with_structured_output(PydanticModel)` for all structured outputs.
- Optional: LangSmith tracing behind an env flag.

### 2. Automated drafting → approval → sending
- **Celery beat `prepare_drafts`** (daily or weekly): select organisations that are due
  (deadline or season window, not yet applied this season, contact info present).
- **Chain:** organisation context + profile + performances → structured
  `ApplicationDraft {subject, body, recipients, performance_ids, reasoning, confidence}`.
  Reuse the prompt logic from `organisations/llm.py`.
- **Storage:** an `Application` with status `DRAFT` and a new field `review_state`
  (`PENDING_APPROVAL` / `APPROVED` / `REJECTED`), plus `generated_by_llm` and `prompt_version`.
- **API:**
  - `POST /applications/{id}/approve/`: accepts optional edits, queues `send_application_email` and saves `sent_message_id`.
  - `POST /applications/{id}/reject/`
  - `POST /applications/{id}/regenerate/` with a feedback text
- **Frontend:** a review queue to edit and approve drafts. It can share UI with the inbound-email review queue.
- **Safety:** nothing is sent without approval, there's a daily send cap, and an organisation is never contacted twice in the same season.

### 3. Response checking
Mostly built already. Remaining:
- Finish the approve/dismiss API and the frontend for `InboundEmail`.
- Make sure `sent_message_id` is saved on send, so header matching works.
- Optional: move the classifier to LangChain structured output for consistency.

### 4. Discovery scraper (LangGraph)
A LangGraph workflow, run weekly by a Celery task:
1. **Generate queries:** turn the profile (discipline, regions, languages) into search queries,
   e.g. "street theatre festival open call 2027 Belgium".
2. **Search:** Tavily / Brave / SerpAPI tools, or the existing Mistral web search, plus seed lists (aggregator sites).
3. **Fetch and clean:** `httpx` + trafilatura, or Playwright for JS-heavy pages.
4. **Extract:** structured
   `OrganisationCandidate {name, type, website, country, contact_emails, application_form_url, deadline, dates, relevance_score, evidence}`.
5. **Dedupe** against existing organisations using `normalize_domain`.
6. **Save** as `DiscoveredOrganisation` (`PENDING_REVIEW`). Approving one creates an `Organisation`, which then feeds step 2.

Proposal: move `apps/scraper` into the backend as a `discovery/` Django app so it shares models and Celery.

### 5. Testing and operations
- Tests use LangChain fake chat models and mocked search/fetch, plus sample `.eml` files and HTML fixtures.
- Make sure Celery beat runs in production.

## Open questions
1. **LangChain scope:** discovery and drafting only, with inbox classification on plain Mistral? Or everything through LangChain?
2. **Search provider for discovery:** Tavily, Brave, SerpAPI, or Mistral web search?
3. **Drafting trigger:** all eligible organisations automatically, or only shortlisted ones?
4. **Scraper location:** move it into the backend as `discovery/`, or keep `apps/scraper` separate?
5. **Form-based applications:** also prepare answers for these, or email applications only for now?
