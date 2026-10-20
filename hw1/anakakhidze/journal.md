# Pattern Journal · Ana Kahidze · Weeks 1–4

These entries were reconstructed on 20 October 2026 from my repository and frontend work. AI helped draft the wording. The repository history and test runs are the evidence. The backend and frontend are not yet integrated.

## Week 1 · Context as Budget

- **Evidence date:** 6 October 2026. The team repository was created that day (commit `68a5c0a`, "Initial commit").
- **Where applied:** In the first week, I started the project by creating the repository, dividing the roles, choosing the idea, and beginning to add foundational repo management files.
- **What I delegated to AI:** I asked AI to help draft `TEAM-CONTRACT.md` based on our team's role assignments and suggest an initial repository structure.
- **How I verified it:** The repository history shows the initial commit on 6 October. The roles were written into `TEAM-CONTRACT.md` on 8 October.
- **Reflection:** Next time, I would explicitly track prompt token budgets and dependency limits from day one before setting up the initial repository.

## Week 2 · Spec Before Code

- **Evidence date:** 19 October 2026 (frontend architecture specification and component design).
- **Where applied:** Before writing the 3D components and UI cards, I defined strict TypeScript types for events (`EventItem`) and filters (`FilterState`) to ensure a well-structured frontend schema.
- **What I delegated to AI:** Generating initial component boilerplate and typing based on my architectural prompt and requirements.
- **How I verified it:** Clean TypeScript compilation with zero type errors across the codebase (`tsc --noEmit`).
- **Reflection:** Since the backend and frontend are not yet connected, I will settle the exact JSON contract shape more thoroughly with the backend team ahead of time to make future integration seamless.

## Week 3 · Uncertainty-Aware UX

- **Evidence date:** 19 October 2026 (UI resilience for incomplete data).
- **Where applied:** In the event card components (`EventCard`) and search interfaces. Because live backend data is not yet connected, I added fallbacks so that missing attributes do not break the layout: a placeholder when an event has no image, and an empty-state message when no events match.
- **What I delegated to AI:** Generating the empty-state and placeholder markup.
- **How I verified it:** Visual testing of the components using the built-in demo events.
- **Reflection:** Going forward, I will add clearer visual indicators on the UI to signal when data is pending or estimated once server calls are integrated.

## Week 4 · Grounded Generation (Frontend Mock and Component Testing)

- **Evidence date:** 20 October 2026 (local demo data and UI component validation).
- **Where applied:** Creating local demo events to validate frontend rendering and interactive UI behaviour independently while the backend API is being finalized. The events are fictional, written in English, and marked as demo.
- **What I delegated to AI:** Generating a small set of fictional demo events for UI verification.
- **How I verified it:** Browser inspection of local rendering on the Next.js development server.
- **Reflection:** While demo-backed lookups allow us to perfect the interactive UI, full RAG and API integration will require a separate suite of end-to-end tests once the frontend and backend are wired together.
