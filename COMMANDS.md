# ProjectGate Alpha Commands

## Self-test

```powershell
python ".\scripts\alpha_selftest.py"
```

## Workspace only

```powershell
python ".\install_projectgate_alpha.py" --dry-run --workspace-root "D:\ProjectGate"
python ".\install_projectgate_alpha.py" --install --workspace-root "D:\ProjectGate"
```

## Compile Project Pack

```powershell
python ".\install_projectgate_alpha.py" --install `
  --workspace-root "D:\ProjectGate" `
  --project-name "MyProject" `
  --project-root "D:\MyProject" `
  --docs-dir "D:\MyProjectDocs" `
  --build-pack
```

## Compile and install Codex Skill

```powershell
python ".\install_projectgate_alpha.py" --install `
  --workspace-root "D:\ProjectGate" `
  --project-name "MyProject" `
  --project-root "D:\MyProject" `
  --docs-dir "D:\MyProjectDocs" `
  --build-pack `
  --build-codex-pack `
  --install-codex-skill
```

## Codex usage

```text
/goal $projectgate -p L: Review this issue and produce an action queue. Do not modify project files.
```

```text
/goal $projectgate -p M: Audit this plan and stop at OWNER_DECISION_REQUIRED if authorization is needed.
```

```text
/goal $projectgate -p H: Deep readonly audit. Use evidence first and do not write project files.
```

## ProjectGate Runtime v0.2

Alpha v0.2.0 adds Runtime Gate support. SOPs and KnownBugRules are no longer passive folders only. Real workflows must create a `TaskRun.json`, load active SOPs / KnownBugRules into the task, pass stage gates, use `REPAIR_AND_RECHECK` on gate failure, and pass a delivery check before final delivery.

## ProjectGate Knowledge Router v0.3

Alpha v0.3.0 adds knowledge routing and learning loops. `L / M / H` now controls SOP / KnownBugRule selection scope, not just cost. Successful reusable TaskRuns can create SOP candidates. Failures can create KnownBugRule candidates. Candidates require owner approval before becoming active.

## ProjectGate Auto Capture v0.4.1

Alpha v0.4.1 adds automatic learning-loop capture. Stage gate / delivery check failures automatically create incidents and KnownBugRule candidates. Successful delivery checks automatically create SOP candidates. The owner only approves or rejects candidates instead of manually writing them. If a similar rule already exists, ProjectGate records whether the active rule was not selected, selected but not enforced, or too coarse.


## Operator Workflow v0.4.1

- Added candidate lifecycle tooling for listing, showing, approving, rejecting, and merging SOP / KnownBugRule candidates.
- Added Project Pack manager for pack info, validation, export, and controlled install.
- Added `projectgate_cli.py` as a unified command wrapper for start, stage, delivery, observe, continuity, candidates, pack, status, and controlled command execution.
- Added root `pg.py` and `pg.bat` entrypoints for shorter local commands.
- Added `pg exec` so ProjectGate-controlled commands can automatically write execution logs and run observation gate.
