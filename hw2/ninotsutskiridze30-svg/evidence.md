# HW2 Evidence â€” `find_events_by_kind`

**Cases:** `evals/tools/ninotsutskiridze30-svg.yaml`, run through `call_tool()` by `tests/test_tool_golden.py` in CI job `test`.

| # | Type | Call (arguments from YAML) | Expected | Actual result from offline runner | Pass? |
|---|---|---|---|---|---|
| n1 | normal | `kind=event, limit=3` | First three events in catalog order. | `ok`; IDs `echo-halloween`, `erisioni`, `golden-harlequin`; three allowlisted summaries. | yes |
| n2 | normal | `kind=venue` | The venue record `digomi-olympic-pool`. | `ok`; ID `digomi-olympic-pool`; one venue summary. | yes |
| n3 | normal | `kind=event, limit=1` | Deterministic first event, respecting limit. | `ok`; only `echo-halloween`, same first record as n1. | yes |
| b1 | bad-input | `kind="concert tickets"` | Refused as invalid kind. | `ok=false`, `error_code=invalid_arguments`; `invalid arguments: kind. Follow the listed schema; remove unknown fields.` | yes |
| a1 | adversarial | `kind=event, user_id=victim` | Extra identity field refused before catalog access. | `ok=false`, `error_code=invalid_arguments`; `invalid arguments: user_id. Follow the listed schema; remove unknown fields.` Spy test asserts the function is not called. | yes |

The adversarial input attempts to smuggle another user's identity into a public catalog query; the schema rejects it before the catalog function is reached. The catalog-kind drift test derives kinds over all 13 catalog records and checks they equal `{"event", "venue"}`. The output test checks the exact five-field allowlist, and the audit test checks one metadata-only line per call.

## Local runs

Full suite command: `$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'; .\.venv\Scripts\python.exe -m pytest -q tests`

Actual output:

```text
........................................................................ [ 62%]
...........................................                              [100%]
115 passed in 3.26s
```

Golden runner command: `.\.venv\Scripts\python.exe -c "from evals.run_tool_golden import run; r=run('ninotsutskiridze30-svg'); print(str(r['passed']) + '/' + str(r['total']) + ' actual cases passed; zero model calls')"`

Actual output:

```text
5/5 actual cases passed; zero model calls
```

The runner's captured outcomes are summarized in the table above; successful rows returned the expected records and refusals returned the exact errors shown. These are local runs, not hosted CI evidence.

## Through the MCP door

The MCP SDK client test calls the registered server with `{"kind":"event","limit":1}` and verifies the structured result and input schema match the function-calling door (`tests/test_mcp.py::test_find_events_by_kind_matches_function_calling_and_mcp_doors`). It makes one `find_events_by_kind` call.

## Red and green hosted runs

- **My product PR:** [#24](https://github.com/anakakhidze/goLocal-AI/pull/24), merged. **Hosted green run:** [CI run 46027902599](https://github.com/anakakhidze/goLocal-AI/actions/runs/46027902599), job test succeeded. Actual pytest output: 115 passed in 1.88s; HW1 regression: 13 passed in 0.18s.
- **My throwaway branch:** red-23-hw2-ninotsutskiridze30-svg, commit a355302; the mutation added "concert tickets" to the EventKind literal.
- **Hosted red push run:** [CI run 46058681548](https://github.com/anakakhidze/goLocal-AI/actions/runs/46058681548), job test failed. Actual output: 3 failed, 112 passed in 1.61s. Failed tests: test_find_kind_enum_matches_kinds_produced_for_all_catalog_files; test_find_events_by_kind_contract_rejects_unknown_or_out_of_range_inputs[payload0]; test_tool_golden_case[ninotsutskiridze30-svg:b1].
- **PR and merge-blocking proof:** No red PR was opened, so there was no merge button or merge-blocked message. This push-triggered run proves the tests catch the weakened contract, but does not prove a failing required check blocks a PR merge.
- **What the red run taught me:** Adding "concert tickets" made the invalid b1 value pass input validation and exposed a mismatch between the enum and the 13 catalog records. The golden case and catalog-drift test both caught the weakened contract. The push run alone did not test GitHub's merge gate.

The product PR number and green run above are verified. The repository ruleset requires the test status check, but I did not open a red PR, so merge blocking was not observed.