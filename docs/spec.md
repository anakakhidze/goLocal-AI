# Spec v1 draft · [PENDING: final product name]

This document records the approved product direction and intended Week 2 first slice. The slice has not been implemented. Fields marked PENDING require team decisions before this can be treated as a complete spec v1.

## Problem

People in Georgia who want a local experience may have to search ticket websites, cultural organizations, venues, and community sources separately. That makes it difficult to find a small set of options that fit their current budget, location, and preferences.

## Users

People seeking local experiences across Georgia. PENDING: the team must define a more specific initial user group for the formal spec.

## Goal

Build a personal AI local discovery agent that understands what a user wants now, recommends a few strong local options with reasons, learns stable preferences over time, and can watch for future experiences. The intended Week 2 slice covers only one request against local fixture data.

## Success criteria

PENDING: measurable success criteria for the broader product. The three approved first-slice acceptance criteria appear below.

## Core feature (Weeks 2 to 4 scope)

The Week 2 core feature is a natural-language discovery request against local JSON event fixtures, one model selection step, and up to three explained recommendations. PENDING: the team has not defined additional Weeks 3 to 4 scope.

## Context list

- The user's natural-language request.
- Local JSON event fixtures for development and automated testing, modeled after event information expected from TKT.ge and Biletebi.ge. Fixture content and exact schema are PENDING; synthetic records must not be presented as verified live listings.
- The approved product constraints and acceptance criteria in this document.
- PENDING: model provider and model. No provider is selected or integrated.

## Acceptance criteria

1. A valid request returns no more than 3 unique recommendations, every returned event must exist in the local fixture, and each recommendation must include a nonempty reason.
2. A missing, empty, or whitespace-only request should return HTTP 400 and make zero model calls.
3. A valid request should make at most one external model API call.

These are approved criteria for the intended slice, not claims that the behavior exists. The proposed input is one natural-language request. The exact route, request/response fields, error body, fixture schema, and model provider are PENDING implementation decisions.

## Napkin math

PENDING: request volume, model, token estimates, prices, and monthly cost. AC3 provides a measurable call-count limit without claiming a currency cost.

## Risks and safety

PENDING: the team must complete the instructor template's two likely failures and one misuse case, with responses, before declaring spec v1 complete.

## Out of scope (for now)

For the Week 2 first slice: live TKT.ge scraping; live Biletebi.ge scraping; GPS; notifications; Watches; long-term personalization; conversation history; ticket purchasing; and a production UI. These exclusions do not remove the broader product vision.

## Verification

Planned verification, not yet implemented: tests for fixture-backed unique recommendations and nonempty reasons (AC1); missing, empty, and whitespace-only requests returning HTTP 400 with zero model calls (AC2); and no more than one external model call for a valid request (AC3). Automated tests must not require live TKT.ge or Biletebi.ge access. PENDING: exact test command and green result, after implementation.

## First slice (Lab 2)

Natural-language request → local JSON fixture → one model call → up to 3 recommendations → short reason for each recommendation.

Criteria: AC1, AC2, AC3 above. Done when: the planned tests for AC1–AC3 pass locally and in CI after an implementation is approved and built. Not in this slice: the items listed under Out of scope.
