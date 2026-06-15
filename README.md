# Make your AI 10^79× stronger

[Why this works](docs/CUBE_MODEL.md)

ProjectGate is an AI workflow gate system that turns unreliable AI output into evidence-backed execution.

It forces AI-assisted work through facts, SOPs, known bug rules, runtime gates, and reviewable TaskRun evidence.

**Current alpha:** v0.4.6

## Start here

Background and problem statement: `BACKGROUND.md` / `BACKGROUND_CN.md`.


Read `QUICKSTART.md` first.

中文文档：`QUICKSTART_CN.md`。

For copy-paste commands, see `COMMANDS.md`.

中文命令速查：`COMMANDS_CN.md`。

## What it gives you

- Core governance rules
- Project Pack compiler
- Codex adapter
- Generic documentation template
- Example docs inbox
- One installer script
- Low / medium / high profile syntax: `-p L`, `-p M`, `-p H`

## What it does not promise yet

- It is not a complete hard-gate system for every AI tool.
- It does not train a model.
- It does not automatically promote rules without owner review.
- It does not modify your project unless you explicitly authorize adapter installation steps.

## Quick install

Initialize a workspace only:

```powershell
python install_projectgate_alpha.py --dry-run --workspace-root "D:\ProjectGate"
python install_projectgate_alpha.py --install --workspace-root "D:\ProjectGate"
```

Compile a project pack from docs:

```powershell
python install_projectgate_alpha.py --install `
  --workspace-root "D:\ProjectGate" `
  --project-name "MyProject" `
  --project-root "D:\MyProject" `
  --docs-dir "D:\MyProjectDocs" `
  --build-pack
```

Build and install a Codex pack:

```powershell
python install_projectgate_alpha.py --install `
  --workspace-root "D:\ProjectGate" `
  --project-name "MyProject" `
  --project-root "D:\MyProject" `
  --docs-dir "D:\MyProjectDocs" `
  --build-pack `
  --build-codex-pack `
  --install-codex-skill
```

Use in Codex:

```text
/goal $projectgate -p L: Review this issue and produce an action queue. Do not modify project files.
```

## ProjectGate Runtime v0.2

Alpha v0.2.0 adds Runtime Gate support. SOPs and KnownBugRules are no longer passive folders only. Real workflows must create a `TaskRun.json`, load active SOPs / KnownBugRules into the task, pass stage gates, use `REPAIR_AND_RECHECK` on gate failure, and pass a delivery check before final delivery.

## ProjectGate Knowledge Router v0.3

Alpha v0.3.0 adds knowledge routing and learning loops. `L / M / H` now controls SOP / KnownBugRule selection scope, not just cost. Successful reusable TaskRuns can create SOP candidates. Failures can create KnownBugRule candidates. Candidates require owner approval before becoming active.

## ProjectGate Auto Capture v0.4.5

Alpha v0.4.5 adds automatic learning-loop capture. Stage gate / delivery check failures automatically create incidents and KnownBugRule candidates. Successful delivery checks automatically create SOP candidates. The owner only approves or rejects candidates instead of manually writing them. If a similar rule already exists, ProjectGate records whether the active rule was not selected, selected but not enforced, or too coarse.


## Operator Workflow v0.4.5

- Added candidate lifecycle tooling for listing, showing, approving, rejecting, and merging SOP / KnownBugRule candidates.
- Added Project Pack manager for pack info, validation, export, and controlled install.
- Added `projectgate_cli.py` as a unified command wrapper for start, stage, delivery, observe, continuity, candidates, pack, status, and controlled command execution.
- Added root `pg.py` and `pg.bat` entrypoints for shorter local commands.
- Added `pg exec` so ProjectGate-controlled commands can automatically write execution logs and run observation gate.

## v0.4.5 Safety Hardening

ProjectGate v0.4.5 clarifies the current enforcement boundary and hardens installer behavior.

ProjectGate is an AI workflow evidence layer for ProjectGate-controlled flows. It is not yet an OS-level sandbox or enterprise compliance platform.

Safety changes:

- ProjectGate-managed directory replacements now use `.projectgate-managed.json` markers.
- Installers refuse to overwrite unmarked non-ProjectGate directories.
- Existing managed directories are backed up before replacement.
- Workspace-root and target-depth checks reduce accidental deletion risk.
- `SECURITY.md` documents the current enforcement boundary and Alpha limitations.


## v0.4.5 Packaging and Test Foundation

ProjectGate v0.4.5 adds a Python package entry point and automated test foundation.

New files:

- `pyproject.toml`
- `projectgate/cli.py`
- `projectgate/__init__.py`
- `tests/test_projectgate_package_and_runtime.py`

`pg.py` is now a compatibility shim. The stable entry point is routed through `projectgate.cli:main`.

The test foundation covers:

- package / pg entry points
- installer safety refusal
- managed replacement backup
- candidate lifecycle
- runtime start / stage / delivery
- observation gate
- pg exec

Run:

```bash
python -m unittest discover -s tests
```


## v0.4.5 Philosophy Docs

ProjectGate v0.4.5 adds philosophy and implementation-map documents.

New docs:

- `docs/WHY_GATES_MATTER.md`
- `docs/CUBE_MODEL.md`
- `docs/IMPLEMENTATION_MAP.md`

These documents explain why gates matter as search-space reduction, present the Cube Model without tying it to a specific private project, and map the philosophy to current ProjectGate implementation files.

## v0.4.5 Headline

ProjectGate v0.4.5 surfaces the Cube Model headline and direct evidence link at the top of the README.

## v0.4.5 Public Surface Sync

ProjectGate v0.4.5 aligns the public homepage with the current Cube Model positioning.

- The README now opens directly with `Make your AI 10^79× stronger`.
- The Cube Model explanation is linked immediately under the headline.
- The first screen now describes ProjectGate as an AI workflow gate system for evidence-backed execution.


## v0.4.6 Documentation Hygiene

ProjectGate v0.4.6 removes private local paths from public documentation.

- Quick Start now points first-time users to the public GitHub repository.
- The Codex adapter README now uses repository-relative paths instead of local machine paths.
- No runtime behavior changes.
