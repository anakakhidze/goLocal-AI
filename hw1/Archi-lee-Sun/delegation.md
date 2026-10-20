# HW1 delegation log · Dated event finder

**20 October 2026 · Tool:** Codex · **Autonomy Ladder:** rung 4 for local implementation; Archil keeps the review and submission decision. The agent has not pushed or merged this work.

**Task delegated.** I asked Codex to implement my complete individual HW1 inside `hw1/Archi-lee-Sun/`: a one-page spec, a working feature, three run-and-record golden questions, tests, a delegation log, and journal entries. The agent used the lecturer's `Lab-3/MILESTONE-1.md`, this team's `AGENTS.md` and `docs/spec.md`, and the dated event-source notes already available in the workspace. The feature deliberately uses a local fixture and no Gemini or database connection.

**What came back wrong, and what caught it.** The first sort test used records already in chronological order, so it would pass without sorting. Reviewing the tests exposed this; I added a reversed-order test. A Windows CLI check also exposed a `UnicodeEncodeError` on a Georgian title. I added a failing regression test, then forced UTF-8 output. Source review showed conflicting HARDHELL venue details, so that record was excluded rather than guessing.

**Verification and decision.** The agent ran `python -m pytest hw1/Archi-lee-Sun -q`: **13 passed**, including blocked-network and Georgian-output checks. It ran all three commands in `golden.md`, recording actual IDs, dates and sources, plus an invalid-date check. The feature makes no network or model call. No shared `AGENTS.md` change was needed. Before submission I will review the diff and request teammate approval for a PR containing only my HW1 folder; CI and human review are not yet claimed as completed.
