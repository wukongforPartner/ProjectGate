# ProjectGate Runtime v0.2

Runtime v0.2 makes SOP / KnownBugRule usage mandatory when a workflow uses ProjectGate.

## Minimal local runtime flow

```powershell
python core/projectgate_core_v0_1/runtime/projectgate_task_start.py `
  --project-pack examples/dreamstory_project_pack_v0_1 `
  --task-type player_feedback_triage `
  --task-title "Test task" `
  -p L `
  --run-root .projectgate_runs

python core/projectgate_core_v0_1/runtime/projectgate_stage_gate.py `
  --taskrun .projectgate_runs/<RUN>/TaskRun.json `
  --stage READONLY_AUDIT `
  --input .projectgate_runs/<RUN>/readonly_audit.md

python core/projectgate_core_v0_1/runtime/projectgate_delivery_check.py `
  --taskrun .projectgate_runs/<RUN>/TaskRun.json
```

Stage outputs must declare:

```text
SOP_USED=<active SOP id or path>
KNOWN_BUG_RULES_CHECKED=<active rule ids or summary>
```

Gate failure means `REPAIR_AND_RECHECK`, not final termination.

## ProjectGate Knowledge Router v0.3

Alpha v0.3.0 adds knowledge routing and learning loops. `L / M / H` now controls SOP / KnownBugRule selection scope, not just cost. Successful reusable TaskRuns can create SOP candidates. Failures can create KnownBugRule candidates. Candidates require owner approval before becoming active.

## ProjectGate Auto Capture v0.4.2

Alpha v0.4.2 adds automatic learning-loop capture. Stage gate / delivery check failures automatically create incidents and KnownBugRule candidates. Successful delivery checks automatically create SOP candidates. The owner only approves or rejects candidates instead of manually writing them. If a similar rule already exists, ProjectGate records whether the active rule was not selected, selected but not enforced, or too coarse.


## Auto Capture v0.4.2

- TaskRun directories are now allocated with microsecond precision and collision retry.
- `projectgate_task_start.py` no longer fails when two same-type runs start within the same second.
- Pre-TaskRun failures can emit a pretask incident and a KnownBugRule candidate when a run root is available.


## TaskRun Continuity v0.4.2

- ProjectGate can detect multiple distinct primary TaskRun paths in a single observed goal transcript.
- `projectgate_taskrun_continuity_gate.py` records `PG-RUNTIME-SINGLE-PRIMARY-TASKRUN-001` when one goal appears to switch TaskRuns without an explicit child-run relationship.
- This prevents reports, stage gates, and delivery checks from silently binding to a different TaskRun than the one created at goal start.


## Operator Workflow v0.4.2

- Added candidate lifecycle tooling for listing, showing, approving, rejecting, and merging SOP / KnownBugRule candidates.
- Added Project Pack manager for pack info, validation, export, and controlled install.
- Added `projectgate_cli.py` as a unified command wrapper for start, stage, delivery, observe, continuity, candidates, pack, status, and controlled command execution.
- Added root `pg.py` and `pg.bat` entrypoints for shorter local commands.
- Added `pg exec` so ProjectGate-controlled commands can automatically write execution logs and run observation gate.
