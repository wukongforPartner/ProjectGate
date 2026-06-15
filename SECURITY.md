# Security Policy

ProjectGate Alpha is an AI workflow evidence layer and controlled runtime toolchain. It is not a system sandbox, an enterprise compliance platform, or an operating-system-level enforcement layer.

## Current enforcement boundary

ProjectGate can enforce rules inside ProjectGate-controlled flows:

- TaskRun creation
- stage gate checks
- delivery checks
- observation gate checks
- TaskRun continuity checks
- `pg exec` controlled command execution
- candidate review / approval / rejection / merge workflows

ProjectGate cannot yet guarantee interception of every action taken by an external AI client that bypasses ProjectGate.

## Destructive action policy

ProjectGate installers and adapters must not delete arbitrary directories.

Beginning in v0.4.1, managed replacements are restricted:

- overwrite targets must be non-root, non-home, and sufficiently deep paths
- overwrite targets must be inside the intended workspace when applicable
- existing ProjectGate-managed directories receive a backup before replacement
- unmarked non-ProjectGate directories are refused
- copied ProjectGate-managed directories receive `.projectgate-managed.json`

## Known Alpha limitations

- Native transcript hooks for all third-party AI clients are not complete.
- ProjectGate-controlled commands are observable; commands run outside ProjectGate are outside this boundary.
- The project is not yet distributed through PyPI or signed release artifacts.
- The test suite is still smoke/selftest oriented and not a full formal verification suite.

## Recommended production stance

Do not use ProjectGate Alpha as a sole security control. Use it as a workflow evidence layer while retaining normal source control, review, sandboxing, backups, and permission controls.
