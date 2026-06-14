# Stage Gate v0.1

## Stages

- INTAKE
- READONLY_AUDIT
- FACT_COLLECTION
- ENTRY_MAP
- ANCHOR_MAP
- PLAN
- WRITE_AUTHORIZATION
- EXECUTION
- VERIFICATION
- HANDOFF

## Rule

A workflow may only perform actions allowed by its current stage. If a task needs a later-stage action, stop and request owner authorization.
