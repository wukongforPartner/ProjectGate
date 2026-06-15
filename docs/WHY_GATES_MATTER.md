# Why Gates Matter

ProjectGate starts from one simple claim:

> A complex task without state, facts, constraints, and error memory is not engineering. It is random search in a large output space.

A gate is not bureaucracy. A gate is a state-space reducer.

## The problem

AI agents can produce fluent output even when they do not know the current state of the project. This creates a dangerous failure mode:

- the agent appears confident;
- the output looks plausible;
- the missing facts are hidden;
- the next action may mutate the project anyway.

In a complex workflow, this is not a small error. It changes the nature of the task.

Without gates, the agent is searching across many possible actions, many possible assumptions, many possible files, many possible commands, and many possible partial fixes.

With gates, the workflow forces the agent to establish state before action.

## What a gate does

A good gate forces a workflow to answer questions such as:

- What facts are confirmed?
- What facts are still unknown?
- Which SOPs apply?
- Which known bug rules apply?
- Which stage is currently allowed?
- Is the next action read-only, mutating, destructive, or release-related?
- What evidence proves that this stage passed?

This does not make the agent smarter. It makes the search space smaller.

## Gates as search-space reduction

Assume a task requires `n` consecutive correct steps.

If each step has `B` plausible actions without state constraints, the unconstrained search space is approximately:

```text
B^n
```

If gates reduce each step to `b` valid candidate actions, the constrained search space is approximately:

```text
b^n
```

The reduction factor is:

```text
(B / b)^n
```

This is why gates matter. Even a modest reduction at each step compounds across the workflow.

## Why this is especially important for AI

A human expert often knows which assumptions are dangerous. An AI agent often continues even when it lacks facts, unless the workflow forces it to stop.

That means every ungated AI workflow risks turning a deterministic engineering problem into an exponential exploration problem.

ProjectGate exists to prevent that collapse.

## What ProjectGate implements

ProjectGate does not ask users to trust that an AI agent will remember the rules. It makes the workflow leave runtime evidence:

- Task state is captured in `TaskRun.json`.
- Project facts are captured in `project_manifest.json`.
- Standard safe paths live in `SOPs/active`.
- Known failure paths live in `KnownBugRules/active` and `Incidents/`.
- Stage checks run through `projectgate_stage_gate.py`.
- Delivery checks run through `projectgate_delivery_check.py`.
- Observation checks run through `projectgate_observation_gate.py`.
- Task continuity checks run through `projectgate_taskrun_continuity_gate.py`.
- Candidate rules are reviewed through `projectgate_candidate_lifecycle.py`.

ProjectGate is an implementation of a general principle:

> Do not let an AI agent act in an undefined state.
