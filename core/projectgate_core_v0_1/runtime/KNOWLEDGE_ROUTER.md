# ProjectGate Knowledge Router v0.3

Knowledge Router prevents SOP and KnownBugRule growth from becoming context overload.

The runtime should not load every SOP and every rule into every task. Instead it should:

1. Build a lightweight index.
2. Select knowledge by profile, task type, stage, and triggers.
3. Record selected IDs in TaskRun.json.
4. Execute machine-checkable gates where possible.
5. Leave candidates inactive until owner promotion.

## Profiles

- `L`: always-on + minimal task-type matches.
- `M`: `L` + stage/tool related knowledge.
- `H`: deep relevant review, but still routed rather than blind full-context loading.

## Success / failure learning loop

- Successful repeatable TaskRun -> SOP candidate.
- Failure / incident -> KnownBugRule candidate.
- Owner approval -> active SOP / active KnownBugRule.

## Auto Capture v0.4.5

Failures no longer only return FAIL. Runtime automatically captures incidents and creates KnownBugRule candidates. Successful delivery checks automatically create SOP candidates. Candidates require owner approval before becoming active.


## Auto Capture v0.4.5

- TaskRun directories are now allocated with microsecond precision and collision retry.
- `projectgate_task_start.py` no longer fails when two same-type runs start within the same second.
- Pre-TaskRun failures can emit a pretask incident and a KnownBugRule candidate when a run root is available.


## TaskRun Continuity v0.4.5

- ProjectGate can detect multiple distinct primary TaskRun paths in a single observed goal transcript.
- `projectgate_taskrun_continuity_gate.py` records `PG-RUNTIME-SINGLE-PRIMARY-TASKRUN-001` when one goal appears to switch TaskRuns without an explicit child-run relationship.
- This prevents reports, stage gates, and delivery checks from silently binding to a different TaskRun than the one created at goal start.
