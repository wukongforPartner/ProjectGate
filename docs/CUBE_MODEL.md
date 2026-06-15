# The Cube Model

The Cube Model explains why workflow gates are not optional overhead in complex AI-assisted work.

It uses a Rubik's Cube as a reference case because a cube is a large but structured state space.

## The key distinction

A cube is not solvable because the state space is small. It is solvable because:

- the current state is visible;
- legal moves are defined;
- invalid moves can be excluded;
- the goal state is known;
- solving methods constrain the next move.

Without those facts, solving becomes blind search.

The same principle applies to software work, design work, release work, and AI-agent workflows.

## Layer 1: random cube state vs constrained solving

A standard 3×3×3 cube has roughly:

```text
4.3 × 10^19
```

reachable states.

However, once the current state is known and legal solving constraints are used, the task is no longer random traversal across all states.

The point is not that every real workflow is a cube. The point is that state and constraints transform the search problem.

## Layer 2: general workflow branching

Let a complex task require `n` consecutive correct steps.

Without gates, each step may have `B` plausible options:

```text
unconstrained = B^n
```

With gates, facts, SOPs, known bug rules, and stage checks reduce each step to `b` valid options:

```text
constrained = b^n
```

The reduction factor is:

```text
(B / b)^n
```

If `B = 15000`, `b = 15`, and `n = 20`, then:

```text
(B / b)^n = (15000 / 15)^20 = 1000^20 = 10^60
```

Combined with the cube reference scale, the difference can reach around:

```text
10^78 to 10^79
```

This number is not a product claim. It is a scale argument.

It shows that missing state and missing constraints do not merely add a little risk. They can change a solvable engineering workflow into an intractable search problem.

## The practical lesson

Every time an AI agent acts without facts, current state, error memory, or stage constraints, the workflow expands its search space.

Every effective gate reduces that space.

That is why gates are not bureaucracy. They are a condition for solving.
