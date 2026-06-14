# Budget Profiles v0.1

## low

Use for smoke tests, triage, and low-cost planning.

- Avoid subagents by default.
- Prefer local scripts over model context.
- Stop early at owner decision.

## medium

Use for normal bounded review.

- Use evidence packs before targeted reads.
- Use subagents only after evidence exists.

## high

Use for deep review.

- Multiple evidence packs allowed.
- Subagents allowed after evidence exists.
- Still requires owner authorization for destructive actions.
