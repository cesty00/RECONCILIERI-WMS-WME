# Repository Routing Lock

Required repository:
cesty00/RECONCILIERI-WMS-WME

Repository lock rule:
All GitHub operations for this project must target only cesty00/RECONCILIERI-WMS-WME.

Mandatory pre-write check:
Before creating a branch, commit, PR, merge, update, or delete operation, the agent must verify:

- repository_full_name == cesty00/RECONCILIERI-WMS-WME
- default_branch == main
- AGENTS.md exists on main

If repository_full_name is anything else, including cesty00/TraceAI-Control, the agent must stop and report:
ROUTING_MISMATCH

The agent must not attempt to "fix" this by writing to the returned repository.

Repository identity:

- repository_id: 1257065922
- default_branch: main
- captured during TASK 0.ROUTING

Future task requirement:
Every future task report must include:

- Repository routing verified: YES / NO
- Repository returned by GitHub tool: ...
- Repository id used, if available: ...
