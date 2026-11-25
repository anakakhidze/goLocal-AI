# Delegation log · [PENDING: product name]

One entry per delegation that mattered. Lives at `docs/delegation-log.md`.

## Entry 1 · HW2 search_events tool contract

- Task: HW2 tool contract: `search_events` contract (extra="forbid", fixed sets, bounds), registry and `call_tool()`, MCP second door, 5 golden cases (3 normal, 1 bad input, 1 adversarial), both-doors tests, CI gate.
- Delegated to: Claude (Haiku 5.5) in Claude Code. Context: the HW2 brief as pasted by the student, the goLocal-AI repo files, and the student's corrections over several rounds.
- Plan check: a file-by-file plan was proposed. The student approved in chat ("do whatever HW2 says") but did not approve the file list before files were written.
- Came back wrong: the first version wrapped an HW1 function, used wrong branch names, and lacked `contract.md`, `evidence.md` and the golden YAML. The MCP door first dropped unknown fields silently until its signature was changed to the pydantic model.
- Caught by: the both-doors test, which failed on the unknown `user_id` field; the student's review of the brief; the weakened-contract run (3 tests fail locally and in CI).
- Decision: rebuilt on the chosen function. Product PR open for teammate review; the weakened-contract throwaway PR was closed without merging.
- AGENTS.md change: none.
- Cost: not measured. Several rebuild rounds.

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
