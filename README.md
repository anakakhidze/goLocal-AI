# goLocal-AI

Working repository name for a planned AI-powered local discovery agent for people across Georgia.

> Status: the full application remains in the companion GoLocal repository. This repository now also contains Archi-lee-Sun's HW2 source-backed event-detail tool, shared MCP/executor frame, offline tests and CI. It does not yet contain the complete frontend/backend application.

## The problem

People looking for local experiences in Georgia may need to check ticket sites, venues, cultural organizations, and community sources separately. The planned product will let them describe what they want naturally and receive a small number of relevant options with reasons for each recommendation.

## Current scope

The full product vision covers discovery across Georgia, conversational refinement, preference learning, and future Watches. The approved Week 2 first slice is documented in [docs/spec.md](docs/spec.md). It is **planned, not built**. TKT.ge and Biletebi.ge are the approved initial real event sources; local JSON fixtures are planned for development and automated tests without live-site dependencies.

HW2 setup, exact test commands, MCP host configuration and verification limits are in [docs/HW2-RUNBOOK.md](docs/HW2-RUNBOOK.md). The tool reads committed historical snapshots; it never claims live ticket availability. CI results and merge approvals must be checked on the corresponding pull requests.

## Team and repository rules

Ana Kahidze (`anakakhidze`) is Repo keeper; Archil Sanikidze (`Archi-lee-Sun`) is Spec keeper; Nino Tsutskiridze (`ninotsutskiridze30-svg`) is Eval keeper from Week 4. See [docs/TEAM-REPO.md](docs/TEAM-REPO.md) for the instructor's repository rules.
