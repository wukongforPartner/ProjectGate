# ProjectGate Runtime v0.2

ProjectGate Runtime 的目标是把 SOP 和 KnownBugRules 从“被动文档”变成“运行时必需输入”。

一个任务不能只靠 AI 自觉说“我会遵守”。任务开始时必须由 `projectgate_task_start.py` 创建 `TaskRun.json`，并记录：

- 已加载的 active SOP
- 已加载的 active KnownBugRules
- 本次任务必须经过的 runtime gates

阶段输出不能只靠模型自评。必须由 `projectgate_stage_gate.py` 检查，并把结果写回 `TaskRun.json`。

如果 gate 失败，下一步不是“结束”，而是 `REPAIR_AND_RECHECK`：把失败原因反馈给 AI，修正后重新检查。

最终交付前必须由 `projectgate_delivery_check.py` 确认 SOP / KnownBugRules 已进入本次 TaskRun，并且至少有一次阶段 gate 通过。

## Auto Capture v0.3.2

失败不再只返回 FAIL。Runtime 会自动捕获 incident，并生成 KnownBugRule candidate。成功的 delivery check 会自动生成 SOP candidate。candidate 需要 owner 批准后才可进入 active。


## Auto Capture v0.3.2

- TaskRun 目录现在使用微秒级时间戳，并带碰撞重试。
- 同一秒内启动两个相同 task type 的运行，不应再因为目录已存在而失败。
- 如果 TaskRun 创建前失败，只要 run root 可写，就会写出 pretask incident 与 KnownBugRule candidate。
