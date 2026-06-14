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
