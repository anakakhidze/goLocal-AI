# goLocal-AI · Spec v1

Status: The first slice is specified but has not been implemented. Targets below are goals, not measured results.

## Problem

People in Georgia who want a local experience may have to search ticket websites, cultural organizations, venues, and community sources separately. That makes it difficult to find a small set of options that fit their current budget, location, and preferences.

## Users

Initial users are Georgian-speaking people looking for local events in Georgia who can describe a preferred city, date, budget, or type of experience in natural language. Initial evaluation uses team-written scenarios and synthetic event data; success does not depend on recruiting public users.

## Goal

Build a personal AI local discovery agent that understands what a user wants now, recommends a few strong local options with reasons, learns stable preferences over time, and can watch for future experiences. The intended Week 2 slice covers only one request against local fixture data.

## Success criteria

1. On 10 team-reviewed natural-language queries with known relevant events in the fixture, at least 8 queries return at least one event marked relevant for that query.
2. Every returned event ID exists in the fixture. At least 90% of recommendation reasons in those 10 queries pass a team review: each reason uses a fact present in that event's fixture record and makes no unsupported factual claim.
3. For a planning scenario of 20 valid requests per day, projected model-only cost is at most USD 2 per 30-day month, calculated from measured average input/output tokens and the published paid Standard prices. This is a cost target, not a claim about actual traffic or free-tier quota.

## Core feature (Weeks 2 to 4 scope)

The approved first slice is text-based event discovery from a local JSON fixture. Later slices may extend the same discovery flow for the course's multimodal and retrieval work; their exact behavior and acceptance criteria require separate team decisions before being added to this living spec.

## Context list

- The user's natural-language request.
- Local JSON event fixtures for development and automated testing, modeled after event information expected from TKT.ge and Biletebi.ge. Fixture content and exact schema are PENDING; synthetic records must not be presented as verified live listings.
- The approved product constraints and acceptance criteria in this document.
- Intended model provider and model for the Week 2 first slice: Gemini Developer API with `gemini-3.1-flash-lite`. This is a planning decision; no provider is integrated yet.

## Constraints

- Python and Django are the approved application stack.
- The first slice uses a local synthetic JSON fixture and Gemini Developer API model `gemini-3.1-flash-lite`, with at most one external model call per valid request.
- Returned event IDs and displayed event facts must come from validated fixture records; model output is not a source of event facts.
- Automated tests use a fake model response and make no external model calls.
- No API keys, personal data, or real user requests are committed to the repository. Until privacy handling is agreed, demonstrations use team-written requests.

## Acceptance criteria

1. A valid request returns no more than 3 unique recommendations, every returned event must exist in the local fixture, and each recommendation must include a nonempty reason.
2. A missing, empty, or whitespace-only request should return HTTP 400 and make zero model calls.
3. A valid request makes at most one external model API call. In a controlled 20-request measurement, the projected model-only cost at 20 valid requests/day over 30 days is no more than USD 2, using observed average token counts and the published paid Standard rates.

These are approved criteria for the intended slice, not claims that the behavior exists. The proposed input is one natural-language request. The exact route, request/response fields, error body, and fixture schema are PENDING implementation decisions.

## Napkin math

Planning scenario only: 20 valid requests/day × 30 days = 600 requests/month. At one call/request, assume 4,000 input and 500 output tokens per call until measured. At the [published paid Standard text rates for Gemini 3.1 Flash-Lite](https://ai.google.dev/gemini-api/docs/pricing), estimated model-only cost is (2.4M × USD 0.25/M) + (0.3M × USD 1.50/M) = USD 1.05/month. This excludes hosting and any additional services. Replace token assumptions with measured averages before claiming the USD 2 target is met. Free-tier availability may reduce actual model charges, but the team's active RPM, TPM, and RPD limits must be checked in [AI Studio](https://ai.google.dev/gemini-api/docs/rate-limits).

## Risks and safety

- Failure 1 — The model selects a nonexistent event or invents an event detail. Response: validate every selected ID against the fixture and construct returned event facts from the fixture; never show invented details.
- Failure 2 — Gemini is unavailable or the project reaches its quota. Response: return an explicit service-unavailable result; do not present fabricated recommendations or make a second model call in the first slice.
- Misuse — A user or fixture text attempts to override instructions or obtain a secret. Response: treat both as untrusted input, never include credentials in prompts or responses, and validate the final IDs against the fixture.

## Out of scope (for now)

For the Week 2 first slice: live TKT.ge scraping; live Biletebi.ge scraping; GPS; notifications; Watches; long-term personalization; conversation history; ticket purchasing; and a production UI. These exclusions do not remove the broader product vision.

## Verification

Planned command after implementation: `python -m pytest -q tests`. Green means exit code 0 locally and in the GitHub Actions `test` job, with tests covering AC1–AC3. Tests must use a fake model and synthetic fixture; they must not require a key, a live event site, or a paid API call. The command and CI result are not yet verified because the application and tests do not exist. The cost portion of AC3 is checked separately with recorded token usage from controlled manual requests.

## First slice (Lab 2)

Natural-language request → local JSON fixture → one model call → up to 3 recommendations → short reason for each recommendation.

Criteria: AC1, AC2, AC3 above. Done when: the planned tests for AC1–AC3 pass locally and in CI, and the controlled cost measurement meets AC3, after an implementation is approved and built. Not in this slice: the items listed under Out of scope.
