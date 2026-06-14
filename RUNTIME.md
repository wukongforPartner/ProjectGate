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
