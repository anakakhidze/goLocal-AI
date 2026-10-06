# AGENTS.md · goLocal-AI (working repository name)

AI coding agents work on a planned local discovery application for people across Georgia. The first slice is documented, not implemented. Feature source of truth: `docs/spec.md`; repository workflow: `docs/TEAM-REPO.md`.

## Commands

- Install: PENDING — no dependency manifest exists.
- Run: PENDING — no Django application exists.
- Test: PENDING — no test suite or verified command exists.
- Lint/format: PENDING — no configuration or verified command exists.

## Conventions

- Python and Django are approved. Inspect the repository before choosing file locations or adding code; no application architecture exists yet.
- First slice: natural-language request, local JSON fixture, at most one external model call for a valid request, and at most three unique fixture-backed recommendations with nonempty reasons. Empty or whitespace-only requests return HTTP 400 and make zero model calls.
- Treat fixtures as synthetic until verified. TKT.ge and Biletebi.ge are planned real sources; neither has a live integration here.
- Validate model-selected event IDs against trusted event data before returning them. The model provider, model selection, call site, structured output shape, and usage logging implementation are PENDING.
- The HTTP 400 error body, event schema, date/time rules, and other units are PENDING. Do not silently choose a public contract.
- Changed behavior needs a test that would fail if it broke. Automated tests must not depend on live event sites or paid model calls.

## Always

- Read `docs/spec.md` and relevant existing files, then propose a small plan and wait for human approval before implementation.
- Keep changes within the approved slice; inspect existing patterns before adding abstractions or refactoring other work.
- Add or update relevant tests, run the verified test command when one exists, and report the actual result or why verification was unavailable.

## Ask first

- Add, remove, or upgrade a dependency; select a model provider or agent framework; add an external API or service.
- Change acceptance criteria, a public response shape, the event schema's public contract, or significant architecture.
- Edit CI configuration; add scraping or new integration sources; request GPS; introduce long-term personalization, Watches, notifications, or ticket purchasing.

## Never

- Read, write, commit, or print `.env` or secrets.
- Delete, skip, or weaken a test to make code pass.
- Fabricate event details or source URLs, or return a model-selected event ID absent from validated source data.
