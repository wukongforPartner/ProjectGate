# ProjectGate Alpha 命令速查

## 自测

```powershell
python ".\scripts\alpha_selftest.py"
```

## 只初始化工作区

```powershell
python ".\install_projectgate_alpha.py" --dry-run --workspace-root "D:\ProjectGate"
python ".\install_projectgate_alpha.py" --install --workspace-root "D:\ProjectGate"
```

## 编译 Project Pack

```powershell
python ".\install_projectgate_alpha.py" --install `
  --workspace-root "D:\ProjectGate" `
  --project-name "MyProject" `
  --project-root "D:\MyProject" `
  --docs-dir "D:\MyProjectDocs" `
  --build-pack
```

## 编译并安装 Codex Skill

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

## Codex 用法

```text
/goal $projectgate -p L: Review this issue and produce an action queue. Do not modify project files.
```

```text
/goal $projectgate -p M: Audit this plan and stop at OWNER_DECISION_REQUIRED if authorization is needed.
```

```text
/goal $projectgate -p H: Deep readonly audit. Use evidence first and do not write project files.
```
