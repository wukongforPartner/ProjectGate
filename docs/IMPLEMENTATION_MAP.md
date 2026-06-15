# ProjectGate Implementation Map

This document maps the gate philosophy to current ProjectGate implementation facts.

It avoids abstract labels that do not exist in the repository. Every entry below points to current ProjectGate concepts or files.

| Gate concept | ProjectGate implementation |
| --- | --- |
| Current task state | `TaskRun.json` |
| Project facts | `project_manifest.json` |
| Standard safe paths | `SOPs/active` |
| Known failure paths | `KnownBugRules/active` |
| Failure evidence | `Incidents/` |
| Stage enforcement | `core/projectgate_core_v0_1/runtime/projectgate_stage_gate.py` |
| Delivery enforcement | `core/projectgate_core_v0_1/runtime/projectgate_delivery_check.py` |
| Observation gate | `core/projectgate_core_v0_1/runtime/projectgate_observation_gate.py` |
| TaskRun continuity | `core/projectgate_core_v0_1/runtime/projectgate_taskrun_continuity_gate.py` |
| Candidate review | `core/projectgate_core_v0_1/runtime/projectgate_candidate_lifecycle.py` |
| Project Pack commands | `core/projectgate_core_v0_1/runtime/projectgate_pack_manager.py` |
| Unified CLI | `projectgate/cli.py`, `pg.py`, `pg.bat` |
| Safety boundary | `SECURITY.md` |
| Automated tests | `tests/test_projectgate_package_and_runtime.py` |

## How the pieces work together

1. A workflow starts by creating a `TaskRun.json`.
2. ProjectGate loads relevant project facts, SOPs, and known bug rules.
3. A stage output must pass the stage gate.
4. Final delivery must pass the delivery check.
5. Runtime observations can create incident and KnownBugRule candidates.
6. Candidates are not active until reviewed.
7. The CLI provides a repeatable operator path.
8. Tests verify that key entry points and safety boundaries keep working.

The goal is not to make an AI agent promise compliance.

The goal is to make the workflow produce checkable evidence.
