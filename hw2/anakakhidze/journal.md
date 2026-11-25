# Pattern Journal · HW2 · anakakhidze

Three dated entries: Weeks 5, 6 and 7.

## Week 5 · 2026-10-28 · Tool Contract

- What the pattern is: defining a strict schema and validation rules around a tool so the model can only pass allowed arguments and cannot bypass limits or supply caller identity itself.
- Where I used it or would use it in my product: I wrapped `search_events` in `goLocal-AI` with input validation (`extra="forbid"`, allowed cities and categories, numeric bounds) and exposed it through both `call_tool()` and the MCP server.
- What went wrong or surprised me: when loosening `extra="forbid"` to `extra="ignore"` during testing, extra fields like `user_id` were not rejected, which showed how easily a loose contract lets unwanted fields through.

## Week 6 · 2026-11-04 · Session State

- What the pattern is: keeping conversation state separate from raw model context with explicit rules for who can read it, how long it stays, when it is written, and how it is deleted.
- Where I used it or would use it in my product: in `goLocal-AI`, any user preference or session state should have clear scope and lifetime rules rather than sitting in one shared history.
- What went wrong or surprised me: state bugs often do not raise errors—things like wrong scope keys, duplicate event firing, or missing flushes can quietly skew data if not checked.

## Week 7 · 2026-11-11 · Supervised Autonomy Loop

- What the pattern is: a loop that takes a goal, runs a few steps on its own, stops after a fixed number of steps, and waits for a person's yes before any action that costs someone something.
- Where I used it today: I focused on completing my HW2 `search_events` tool contract, golden tests, and documentation while reviewing how the supervised autonomy loop fits into the capstone.
- The one action in my product that must wait for a yes: any action that makes a real commitment or change (such as confirming a booking or sending a request), unlike `search_events` which only reads event data.
