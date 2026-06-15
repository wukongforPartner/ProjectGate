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

## ProjectGate Knowledge Router v0.3

Alpha v0.3.0 新增知识路由与沉淀闭环：`L / M / H` 不再只是成本标签，也决定 SOP / KnownBugRule 的选择范围。成功且可复用的 TaskRun 可以生成 SOP candidate；失败事故可以生成 KnownBugRule candidate；candidate 必须 owner 批准后才进入 active。

## ProjectGate Auto Capture v0.4.3

Alpha v0.4.3 新增自动沉淀闭环：stage gate / delivery check 失败会自动生成 incident 和 KnownBugRule candidate；delivery check 成功会自动生成 SOP candidate。owner 只负责 approve / reject，不再负责手写候选规则。若已有同类规则，系统会记录是 active 规则未被选中、已选中但未执行、还是规则粒度不够。


## Auto Capture v0.4.3

- TaskRun 目录现在使用微秒级时间戳，并带碰撞重试。
- 同一秒内启动两个相同 task type 的运行，不应再因为目录已存在而失败。
- 如果 TaskRun 创建前失败，只要 run root 可写，就会写出 pretask incident 与 KnownBugRule candidate。


## TaskRun Continuity v0.4.3

- ProjectGate 可以检测同一个观察到的 goal transcript 中出现多个不同主 TaskRun 路径。
- `projectgate_taskrun_continuity_gate.py` 会在单个 goal 未声明 child run 却切换 TaskRun 时记录 `PG-RUNTIME-SINGLE-PRIMARY-TASKRUN-001`。
- 这用于防止报告、stage gate、delivery check 悄悄绑定到不同于 goal start 的 TaskRun。


## Operator Workflow v0.4.3

- 新增 candidate 生命周期工具，支持列出、查看、批准、拒绝、合并 SOP / KnownBugRule candidates。
- 新增 Project Pack 管理工具，支持 pack info、validate、export、controlled install。
- 新增 `projectgate_cli.py` 统一命令入口，覆盖 start、stage、delivery、observe、continuity、candidates、pack、status 与受控命令执行。
- 新增根目录 `pg.py` 与 `pg.bat`，减少本地长命令。
- 新增 `pg exec`，让 ProjectGate 受控命令自动写执行日志并运行 observation gate。
