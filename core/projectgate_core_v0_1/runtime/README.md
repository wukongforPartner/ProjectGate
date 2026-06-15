# ProjectGate Runtime v0.2

ProjectGate Runtime turns SOPs and KnownBugRules from passive documentation into required runtime inputs.

A task is not considered properly started unless `projectgate_task_start.py` creates `TaskRun.json` and records:

- loaded active SOPs
- loaded active KnownBugRules
- required runtime gates

A stage output is not considered valid unless `projectgate_stage_gate.py` checks it and records the result in `TaskRun.json`.

If the gate fails, the next action is `REPAIR_AND_RECHECK`, not silent termination. The AI should repair the output according to the fail reasons and rerun the gate.

A final deliverable is not considered valid unless `projectgate_delivery_check.py` confirms that SOPs/rules were loaded and at least one passing gate exists.

## Auto Capture v0.4.1

Failures no longer only return FAIL. Runtime automatically captures incidents and creates KnownBugRule candidates. Successful delivery checks automatically create SOP candidates. Candidates require owner approval before becoming active.


## Auto Capture v0.4.1

- TaskRun directories are now allocated with microsecond precision and collision retry.
- `projectgate_task_start.py` no longer fails when two same-type runs start within the same second.
- Pre-TaskRun failures can emit a pretask incident and a KnownBugRule candidate when a run root is available.


## TaskRun Continuity v0.4.1

- ProjectGate can detect multiple distinct primary TaskRun paths in a single observed goal transcript.
- `projectgate_taskrun_continuity_gate.py` records `PG-RUNTIME-SINGLE-PRIMARY-TASKRUN-001` when one goal appears to switch TaskRuns without an explicit child-run relationship.
- This prevents reports, stage gates, and delivery checks from silently binding to a different TaskRun than the one created at goal start.


## Operator Workflow v0.4.1

- Added candidate lifecycle tooling for listing, showing, approving, rejecting, and merging SOP / KnownBugRule candidates.
- Added Project Pack manager for pack info, validation, export, and controlled install.
- Added `projectgate_cli.py` as a unified command wrapper for start, stage, delivery, observe, continuity, candidates, pack, status, and controlled command execution.
- Added root `pg.py` and `pg.bat` entrypoints for shorter local commands.
- Added `pg exec` so ProjectGate-controlled commands can automatically write execution logs and run observation gate.
