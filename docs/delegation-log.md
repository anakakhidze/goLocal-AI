# Delegation log · goLocal-AI

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

## Entry 2 · HW2 search_events tool (anakakhidze)

- **Task:** HW2 tool contract for `search_events`: strict input contract, lookup over GoLocal's fictional demo fixture, golden set in the shared runner, and the shared CI gate.
- **Delegated to:** Claude (Haiku 5.5) in Claude Code. Context: the HW2 brief as pasted by the student, the GoLocal fixture and filter rules, the shared registry and runner from main, and the student's corrections over several rounds.
- **Plan check:** a file-by-file plan was proposed. The student approved in chat but did not approve the file list before files were written.
- **Came back wrong:** the first version wrapped an HW1 function and used its own registry and MCP server, which clashed with the shared frame. Later, a weakened contract was committed directly to the product branch by mistake and reverted.
- **Caught by:** the shared golden runner and both-doors tests; the student's review; the weakened-contract runs; CI.
- **Decision:** use the shared registry, runner and MCP server, with one tool entry and one golden file.
- **AGENTS.md change:** none.
- **Cost:** not measured. Several rebuild rounds.

## Entry 3 · HW2 find_events_by_kind tool (ninotsutskiridze30-svg) — 2026-11-27

- **Task:** wrap the catalog's event/venue kind filter as a read-only MCP tool with a closed contract, five CI golden cases, a metadata-only audit trail, and a separate personal write-up.
- **Delegated to:** Codex, with the Lab 5 brief and examples, Archi-lee-Sun's HW2 files as a shape reference, current repository rules/tests/CI, and all 13 curated catalog files.
- **Plan check:** Nino approved the revised file-level plan for issue #23 and added the exact enum, golden scenarios, and spy-test requirements before implementation.
- **Came back wrong:** the first write-up draft was placed in a separate `goLocal-AI-writeup` location instead of the team repo's required `goLocal-AI/hw2/ninotsutskiridze30-svg/` folder.
- **Caught by:** Nino checked the primary team repo, noticed the write-up was missing there, and redirected the files into the required folder. The final product implementation was checked with the full local test suite (115 passed) and the offline golden runner (5/5 passed); no golden case was removed or weakened.
- **Decision:** use the catalog's derived `Literal["event", "venue"]` values; return only id, title, kind, source URL, and snapshot date. No source text or identity input is exposed.
- **AGENTS.md change:** none.
- **Cost:** not timed; no live source or model calls. Product PR #24 merged and its hosted green run succeeded; my throwaway red-run proof remains pending.
