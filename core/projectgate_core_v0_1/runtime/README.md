# ProjectGate Runtime v0.2

ProjectGate Runtime turns SOPs and KnownBugRules from passive documentation into required runtime inputs.

A task is not considered properly started unless `projectgate_task_start.py` creates `TaskRun.json` and records:

- loaded active SOPs
- loaded active KnownBugRules
- required runtime gates

A stage output is not considered valid unless `projectgate_stage_gate.py` checks it and records the result in `TaskRun.json`.

If the gate fails, the next action is `REPAIR_AND_RECHECK`, not silent termination. The AI should repair the output according to the fail reasons and rerun the gate.

A final deliverable is not considered valid unless `projectgate_delivery_check.py` confirms that SOPs/rules were loaded and at least one passing gate exists.
