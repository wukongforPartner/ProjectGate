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

## ProjectGate Runtime v0.2

Alpha v0.2.0 新增 Runtime Gate：SOP 和 KnownBugRules 不再只是文档结构。真实工作流必须先生成 `TaskRun.json`，把 active SOP / KnownBugRules 载入本次任务；阶段输出必须通过 stage gate；失败时进入 `REPAIR_AND_RECHECK`，修正后重新检查；最终交付前必须通过 delivery check。

## ProjectGate Knowledge Router v0.3

Alpha v0.3.0 新增知识路由与沉淀闭环：`L / M / H` 不再只是成本标签，也决定 SOP / KnownBugRule 的选择范围。成功且可复用的 TaskRun 可以生成 SOP candidate；失败事故可以生成 KnownBugRule candidate；candidate 必须 owner 批准后才进入 active。

## ProjectGate Auto Capture v0.3.2

Alpha v0.3.2 新增自动沉淀闭环：stage gate / delivery check 失败会自动生成 incident 和 KnownBugRule candidate；delivery check 成功会自动生成 SOP candidate。owner 只负责 approve / reject，不再负责手写候选规则。若已有同类规则，系统会记录是 active 规则未被选中、已选中但未执行、还是规则粒度不够。
