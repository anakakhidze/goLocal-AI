# Delegation log · [PENDING: product name]

One entry per delegation that mattered. Lives at `docs/delegation-log.md`.

## Entry 1 · Archi-lee-Sun HW2 tool and missing shared frame — 2026-11-23

- **Task:** implement and upload Archil's individual HW2 into `anakakhidze/goLocal-AI`, including the missing common registry/executor/MCP/CI prerequisites; leave HW1 and teammates' personal folders unchanged.
- **Delegated to:** Codex, with the official Labs 5/7 briefs, repository AGENTS/spec/workflow and the existing GoLocal corpus. AI assistance is disclosed; the requester retains ownership, explanation, review and submission responsibilities.
- **Plan check:** the product/write-up separation and exact areas (`src/`, `tests/`, `evals/tools/`, CI and personal write-up) were announced in the session after explicit implementation/upload authorization. No broad application rewrite or teammate homework was added.
- **Came back wrong:** the first corpus parser recognized only singular “public listing”, but one existing document says “public listings”. Also, blocking every socket connection prevented Windows asyncio's local socketpair. The first suite reported 17 failures and 65 passes.
- **Caught by:** actual pytest execution. The parser now recognizes both reviewed metadata spellings and preserves alternate event-time/location labels; test networking permits only loopback for local transports while denying external connections. No tests or golden requirements were removed.
- **Decision:** use the documented SDK 2.3 low-level Server to share exact schemas and audit every rejected call. The corrected initial suite passed 82 tests before adding the real subprocess transport regression. CI, branch-rule enforcement and teammate approval are documented separately from local test results.
- **AGENTS.md change:** added real HW2 commands, identity/path boundaries and the prohibition on consequential tools without a separately reviewed gate.
- **Cost:** local implementation/testing time; offline checks require no paid model calls. No human lab attendance, past approval or form submission is inferred.

## Entry template (not an entry)

### Entry N · [task in five words]

- Task: [which acceptance criteria]
- Delegated to: [tool, model, what context it had]
- Plan check: [what you changed before approving, or "approved as proposed"]
- Came back wrong: [be specific; "nothing" only if you say what you checked]
- Caught by: [which gate: plan, tests-first reading, running tests, CI, a teammate]
- Decision: [merged, fixed, rejected and re-delegated]
- AGENTS.md change: [the line you added, or why none was needed]
- Cost: [minutes, extra runs]
