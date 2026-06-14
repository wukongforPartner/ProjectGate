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

## ProjectGate Auto Capture v0.3.2

Alpha v0.3.2 adds automatic learning-loop capture. Stage gate / delivery check failures automatically create incidents and KnownBugRule candidates. Successful delivery checks automatically create SOP candidates. The owner only approves or rejects candidates instead of manually writing them. If a similar rule already exists, ProjectGate records whether the active rule was not selected, selected but not enforced, or too coarse.


## Auto Capture v0.3.2

- TaskRun directories are now allocated with microsecond precision and collision retry.
- `projectgate_task_start.py` no longer fails when two same-type runs start within the same second.
- Pre-TaskRun failures can emit a pretask incident and a KnownBugRule candidate when a run root is available.
