# ProjectGate Workflow State Machine v0.1

Status: static-table first cut.

ProjectGate is a workflow state machine, not a command pile. The Owner starts tasks and provides only Owner-exclusive input: goals, unavailable facts, permissions, risk decisions, and product judgment. Internally repairable failures must stay inside the workflow and be recorded in StateStore / GateHistory instead of being delegated to the Owner.

## First-cut boundary

This cut adds static workflow tables, a pure validator, and tests. It does not implement Orchestrator, modify runtime gates, change adapters, change project packs, or install Qoder hooks.

## Core states

The required state table is stored in `core/projectgate_core_v0_1/workflow/workflow_state_table.json`. It includes `INTERNAL_REPAIR_LOOP`, which is hidden from the Owner by default.

## Owner boundary

The Owner is not an exception handler, command operator, window manager, or AI quality inspector. The Owner is only asked for intent, unavailable facts, permissions, risk decisions, product judgment, or a stop/continue decision.

## Validation

Run:

```bash
python core/projectgate_core_v0_1/workflow/projectgate_workflow_validator.py --root .
python -m unittest discover -s tests
```
