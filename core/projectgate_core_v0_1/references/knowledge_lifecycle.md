# Knowledge Lifecycle v0.1

## SOP lifecycle

```text
SOP_CANDIDATE -> owner review -> ACTIVE_SOP -> loaded in matching tasks
```

## Incident lifecycle

```text
INCIDENT -> known bug rule candidate -> owner review -> ACTIVE_KNOWN_BUG_RULE -> gate check
```

## Unknown task type

If no task type or SOP matches a task, enter read-only discovery and generate a candidate task type and candidate SOP.
