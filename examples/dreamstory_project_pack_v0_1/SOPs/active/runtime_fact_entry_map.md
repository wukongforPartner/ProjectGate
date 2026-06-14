# SOP: Runtime Fact Entry Map

## Trigger

Any task involving runtime facts, analytics events, event fields, or gameplay fact reporting.

## Required process

1. Stay in read-only audit.
2. Search all real code entry points that may produce the mechanism.
3. Classify each entry by path, method, line, trigger mechanism, RuntimeGridItem creation, inventory addition, grid placement attempt, origin marker, and category.
4. Do not define event names or fields before classification is complete.
5. If only partial entry coverage is possible, mark event semantics as partial.

## Stop conditions

- Missing entry map.
- Unknown entry category.
- User asks how you know only one path exists.
