# goLocal-AI · Product spec and implementation status

**Snapshot:** 20 October 2026 · **Spec keeper:** Archil Sanikidze.

This living spec describes the application implemented in the separate [GoLocal repository, `main` at `51aa2c2`](https://github.com/ninotsutskiridze30-svg/GoLocal/tree/51aa2c2). That commit includes the frontend, database foundation, discovery, poster and RAG branches. This **goLocal-AI** repository holds team/course documentation and individual homework; the application code has not been integrated into its `main`. Some older GoLocal documents still call implemented functions pending, so the pinned source is the evidence for current behavior.

## Problem, users and goal

People in Georgia looking for local experiences must compare separate listings, venues and cultural organizations. The primary user describes a city, date, budget or interest in ordinary language and needs a small set of relevant options with reasons and sources. A second workflow helps a curator turn a photographed event poster into structured facts for human review.

The intended product combines browsing, saved events, natural-language discovery, source-grounded answers and poster extraction. Long-term preferences, Watches and notifications remain goals, not features demonstrated by the current browser saves or database demo tables. Gemini-generated recommendations and answers are requested in Georgian; the current frontend UI copy is mainly English.

## Current architecture and data flow

| Component | Implemented in GoLocal | Boundary |
|---|---|---|
| Frontend | Next.js App Router, React/TypeScript, browse/detail/saved pages, filters, search UI and schematic map | Calls an expected HTTP API; no server routes are implemented. Falls back to fictional previews. |
| Database | Docker PostgreSQL with PostGIS and pgvector, migrations, normalization and demo seed scripts | Local development data; no deployed backend or live collector. |
| Discovery | Rule-based parser, parameterized PostgreSQL search, one batched Gemini recommendation call | Fixture-backed fictional events only; no semantic vector search in this path. |
| Posters | Image processing, Gemini vision extraction, evidence checks and CLI | Human-review JSON; no upload UI or automatic database import. |
| RAG | Public-listing Markdown snapshots, local embedding index, hybrid retrieval, grounded answer and CLI | Index lives in a local file, separate from PostgreSQL and the frontend. |

There is no working browser → HTTP service → Python/database/model connection in this snapshot. A frontend fallback search matches local samples; it is not an LLM call. No Django or FastAPI application has been implemented.

### Frontend

The [frontend](https://github.com/ninotsutskiridze30-svg/GoLocal/tree/51aa2c2/frontend) implements `/`, `/events/[id]` and `/saved`, including category, mood, date, budget, free-only and saved-only filters. The map is schematic and not to scale. `frontend/lib/demo-events.ts` holds 14 fictional previews, distinct from the 25 database fixtures. The [event hook](https://github.com/ninotsutskiridze30-svg/GoLocal/blob/51aa2c2/frontend/hooks/useEventEngine.ts) shows preview mode when API requests fail. Saved event objects use browser `localStorage`, not database accounts; if storage is unavailable, they last only for the page visit.

The [API client](https://github.com/ninotsutskiridze30-svg/GoLocal/blob/51aa2c2/frontend/lib/api.ts) expects `GET /events`, `GET /events/{id}` and `POST /search` with `{query}` at `NEXT_PUBLIC_API_BASE_URL` or localhost port 8000. These are client expectations, not implemented endpoints. Browser/build verification remains outstanding.

### Database and datasets

`migrations/001_schema.sql` and `002_seed.sql` establish cities, categories, venues, events, source/provenance records, embeddings and user/activity storage contracts. [Data-layer code](https://github.com/ninotsutskiridze30-svg/GoLocal/tree/51aa2c2/src/golocal_data) normalizes timezone-aware instants, decimal prices and source fields. Unknown price is `null`; zero means free. Source-approval triggers protect source and raw-record writes.

`data/demo_events.json` has 25 fictional `[DEMO]` events, six fictional venues and `example.com` placeholder links. `scripts/seed_demo.py` loads these into PostgreSQL; migrations do not load them automatically. Optional `data/demo_users.json` activity fixtures include fictional users and 15-dimensional category indicators labelled as synthetic, not real semantic embeddings. The frontend's 14 previews are a separate dataset.

The [RAG corpus](https://github.com/ninotsutskiridze30-svg/GoLocal/tree/51aa2c2/data/corpus/events) contains 13 manually compiled public-listing snapshots: 12 event-related documents and one pool/venue document, each with a source URL. These are snapshots, not live inventory or proof of current price/availability. Five real JPG posters and `data/posters/posters.json` record six manually reviewed visible sessions; three extra photo candidates are under `tests/images/candidates/`. Neither corpus nor poster reference JSON is imported into the event database. RAG citations identify documents/chunks, not database event IDs.

## Feature contracts

### Discovery

The implemented [discovery module](https://github.com/ninotsutskiridze30-svg/GoLocal/blob/51aa2c2/src/golocal_data/discovery.py) has these boundaries:

1. `parse_query(query, *, today=None) -> Filters`: validates a nonblank request of at most 2,000 characters and recognizes limited Georgian/English category, keyword, Tbilisi/Batumi, free/GEL budget, and today/tomorrow/day-after-tomorrow terms. Relative dates use `Asia/Tbilisi`. Unrecognized wording is not guessed into hard constraints. No model call occurs.
2. `search_events(filters, query_embedding=None, ...) -> list[EventCandidate]`: parameterized SQL returns at most 12 active, fixture-backed demo candidates. An actual query embedding is rejected because this discovery path does not have configured semantic search. A budget excludes unknown prices and other currencies.
3. `explain(query, candidates, ...) -> list[Recommendation]`: one `gemini-3.1-flash-lite` request for all candidates asks for Georgian reasons. Schema validation, trusted-ID lookup and duplicate removal yield at most three unique results with nonblank reasons. Event facts come from the database candidates. Empty candidates make zero model calls. ID validation alone cannot prove every free-text reason is factual.
4. `recommend(...)` composes the functions; `scripts/recommend.py` exposes a demo-labelled CLI. Invalid input raises a validation error and provider failure becomes a sanitized error, not an HTTP response.

Discovery calls Gemini directly via `httpx` and `GOOGLE_API_KEY` in the environment; this path has no automatic retry or shared usage log.

### Poster extraction

The [poster contract](https://github.com/ninotsutskiridze30-svg/GoLocal/blob/51aa2c2/docs/multimodal-spec.md) accepts JPEG/PNG/WebP up to 10 MB and 24 megapixels, corrects orientation and limits the longest side to 1,024 pixels. One Gemini vision call per image requests JSON fields carrying `{value, evidence, confidence}`. Multiple visible event sessions are supported. Missing/unreadable facts stay null; a ticket logo is not a source URL, an absent year is not inferred, and a doors-open time is not the event start.

`decide(extraction, today)` returns `accepted`, `confirm`, `review` or `rejected`. `safe_draft` clears flagged fields; evidence and format checks precede confidence, and confidence below 0.6 flags uncertainty. Nonposters yield no draft. The CLI returns JSON for human review; `accepted` does not mean a person approved or imported an event. The five real posters are reference material. A successful live vision evaluation and the formal four-photo course set are still pending.

### Source-grounded RAG

The [retrieval contract](https://github.com/ninotsutskiridze30-svg/GoLocal/blob/51aa2c2/docs/retrieval-spec.md) chunks Markdown at headings, with up to 1,200 content characters and 180 overlap, preserving title, section, stable chunk ID and URL. The recorded index contains 26 chunks from 13 documents. `gemini-embedding-2` creates 768-dimensional chunk and query vectors. The ignored `logs/rag_index.json` records model/dimension, metadata and document hashes; stale or mismatched indexes are rejected.

Hybrid retrieval weights cosine similarity 0.75 and normalized BM25 0.25, taking at most five chunks with score at least 0.45. These values are provisional. With no passing chunk, answer generation is skipped, though question embedding still happens. `gemini-3.1-flash-lite` then returns JSON `{answer,citations,grounded}`. Code requires `grounded=true`, valid schema and sentence-ending `[n]` markers that map exactly to retrieved chunks; it attaches trusted source URLs itself. Invalid or unavailable answers refuse. Citation validation proves source provenance, not that every statement is semantically true.

RAG retries transient HTTP 429/500/502/503/504, timeout or transport failures up to three generation attempts, with 2- and 4-second waits. Permanent errors and malformed replies are not retried. Local answer/usage logs record outcomes, attempt counts, retrieved/cited IDs and token/latency estimates without storing prompts, answers or credentials. `scripts/index_corpus.py` and `scripts/ask_corpus.py` are local CLIs; there is no RAG HTTP endpoint.

## Success criteria and evidence

| Criterion | Verified status |
|---|---|
| Discovery: at most three unique trusted events with nonblank reasons; invalid input has zero model calls; a valid request makes at most one generation call. | Covered by offline tests. The old HTTP 400 acceptance criterion remains **unimplemented**; CLI validation exists, while GoLocal's draft API contract proposes HTTP 422. Resolve the response contract before adding routes. |
| Discovery relevance: at least 8/10 reviewed scenarios return a relevant event; at least 90% of reasons pass factual review. | Retained product targets from v1. No completed discovery relevance/reason audit is claimed. RAG's golden score does not measure this. |
| RAG: source-backed citation or deliberate refusal; at least 0.70 on ten golden questions. | Third committed live report scored 9/10 under the original scorer. Source-based audit is 8/10 because a provider timeout was incorrectly accepted as a refusal pass. The corrected scorer rejects provider failures as refusal successes; no fourth live run is recorded. |
| Poster: uncertain fields are cleared; nonposters are rejected. | Offline policy/schema/image tests exist. Live vision quality and formal photo-set completion are outstanding. |

GoLocal's offline suite recorded **186 passing pytest tests** with fake providers and no paid calls or live ticket sites. This does not establish frontend behavior, live model reliability, a particular running database state or deployment. See the [tests](https://github.com/ninotsutskiridze30-svg/GoLocal/tree/51aa2c2/tests), [golden reports](https://github.com/ninotsutskiridze30-svg/GoLocal/tree/51aa2c2/evals/results) and [design review](DESIGN-REVIEW.md).

## Budget, safety and next work

The earlier discovery target remains **USD 2 model-only per 30 days at 20 valid requests/day**, contingent on a controlled 20-request measurement of discovery token usage. Discovery does not yet log usage, so this target is unverified. The review's RAG median-generation projection excludes embeddings, failures/retries, index rebuilding and hosting; it cannot prove the discovery budget. Poster pilot targets below USD 0.02 and 45 seconds per image are also unverified by a successful live vision run.

Treat requests, source documents and poster text as untrusted. Use parameterized SQL, validate model-selected IDs and citation markers, keep keys outside version control and prompts, and clearly label fictional preview data and stale snapshots. Public performer names in the real corpus were retained deliberately; compatibility with the course's shareable-corpus guidance remains to be resolved before submission.

Next integration work is to agree the HTTP contract, expose Python services, reconcile frontend event/error shapes and test browser-to-service behavior. No live TKT.ge/Biletebi.ge collector, poster import, auth, account synchronization, GPS request, conversation history, long-term personalization, Watches, notifications or ticket purchase flow is implemented. The team also needs to resolve the split between its implementation and course repositories through separate reviewed changes.
