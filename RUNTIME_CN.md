# ProjectGate Runtime v0.2

Runtime v0.2 让 SOP / KnownBugRule 在 ProjectGate 工作流中成为必需运行时输入，而不是放在目录里的说明书。

## 最小本地 runtime 流程

```powershell
python core/projectgate_core_v0_1/runtime/projectgate_task_start.py `
  --project-pack examples/dreamstory_project_pack_v0_1 `
  --task-type player_feedback_triage `
  --task-title "Test task" `
  -p L `
  --run-root .projectgate_runs

python core/projectgate_core_v0_1/runtime/projectgate_stage_gate.py `
  --taskrun .projectgate_runs/<RUN>/TaskRun.json `
  --stage READONLY_AUDIT `
  --input .projectgate_runs/<RUN>/readonly_audit.md

python core/projectgate_core_v0_1/runtime/projectgate_delivery_check.py `
  --taskrun .projectgate_runs/<RUN>/TaskRun.json
```

阶段输出必须声明：

```text
SOP_USED=<active SOP id or path>
KNOWN_BUG_RULES_CHECKED=<active rule ids or summary>
```

Gate 失败代表 `REPAIR_AND_RECHECK`：按失败原因修正并重新检查，不是把任务直接结束。
