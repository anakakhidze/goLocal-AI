# Run Archi-lee-Sun's HW2 product slice

Python 3.11+; run from this repository root. The source corpus is committed, and
the tool/server/tests require no database, ticket-site access or model key.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-hw2.txt
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
.\.venv\Scripts\python.exe -m pytest -q tests
.\.venv\Scripts\python.exe -m pytest -q hw1/Archi-lee-Sun
.\.venv\Scripts\python.exe -m src.cli tool get_event_details '{"event_id":"valerian-shiukashvili"}'
.\.venv\Scripts\python.exe -m src.cli mcp-smoke
```

On Linux/macOS, use `.venv/bin/python`. `logs/` is ignored. Set `GOLOCAL_TOOL_LOG`
and `GOLOCAL_USAGE_LOG` in the process to relocate logs; these are server choices,
not fields accepted from the model.

## Connect an MCP host

From this repo root, register stdio command `.venv/Scripts/python.exe` with args
`-m src.mcp_server` (use an absolute Python path and this repo as cwd).
For Claude Code, for example:

```text
claude mcp add --transport stdio golocal -- C:/path/to/goLocal-AI/.venv/Scripts/python.exe -m src.mcp_server
```

`/mcp` should list `list_events` and `get_event_details`. Ask:
"Show the original source and historical entry details for Valerian Shiukashvili."
The reply must retain the snapshot warning, not claim current ticket availability.
An SDK stdio-client smoke test verifies transport; an interactive host/model run
must be recorded separately if no live host/key is available here.

HTTP alternative: `python -m src.mcp_server --http`, then connect to
`http://127.0.0.1:8001/mcp`. Local function-calling demo endpoint:
`python -m src.app` (`GET /tools`, `POST /act` with only `{question: ...}`).
This localhost-only demo is not the full frontend/backend integration or production auth.

## Optional real Gemini turn

Export `GOOGLE_API_KEY` in your own process environment without printing it;
do not commit it or ask the agent to read `.env`. Then:

```text
python -m src.cli ask "List the event IDs, then show the source and details for Valerian Shiukashvili."
```

The adapter keeps the existing `gemini-3.1-flash-lite` model. Check one tool audit
line per call and a sanitized usage line per provider request. No live success is
claimed by offline tests. Native provider reasoning fields are preserved between turns.

## Submission boundary

Product branch: `slice-13-hw2-Archi-lee-Sun`. The `.github/` change needs Repo keeper
review. Write-up branch: `hw2-Archi-lee-Sun`, changing only the individual's folder.
Both PRs need a teammate's review and merge, then the individual submits the Teams form.
Never merge the deliberately weakened red branch. The repo owner must require CI
job `test`; only a genuinely enforced status proves that red CI blocks a merge.

HW2's old 8 November deadline is superseded by Lab 7 + seven days at 23:59 Tbilisi.
25 November applies if the Lab 7 session was 18 November; confirm the Teams announcement.
