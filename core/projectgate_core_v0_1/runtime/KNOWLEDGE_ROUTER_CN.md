# ProjectGate Knowledge Router v0.3

Knowledge Router 用来防止 SOP 和 KnownBugRule 增长后把任务上下文撑爆。

Runtime 不应该每次读取全部 SOP 和全部错误门禁，而应该：

1. 构建轻量索引。
2. 按 profile、task type、stage、trigger 选择相关知识。
3. 把被选择的规则 ID 写入 TaskRun.json。
4. 能机器检查的尽量机器检查。
5. candidate 未经 owner 批准不得进入 active。

## Profiles

- `L`：always-on + 当前任务类型的最小匹配规则。
- `M`：`L` + 阶段 / 工具相关规则。
- `H`：深度相关审查，但仍然不是盲目全量加载。

## 成功 / 失败沉淀闭环

- 成功且可复用的 TaskRun -> SOP candidate。
- 失败 / 事故 -> KnownBugRule candidate。
- owner 批准 -> active SOP / active KnownBugRule。

## Auto Capture v0.4.3

失败不再只返回 FAIL。Runtime 会自动捕获 incident，并生成 KnownBugRule candidate。成功的 delivery check 会自动生成 SOP candidate。candidate 需要 owner 批准后才可进入 active。


## Auto Capture v0.4.3

- TaskRun 目录现在使用微秒级时间戳，并带碰撞重试。
- 同一秒内启动两个相同 task type 的运行，不应再因为目录已存在而失败。
- 如果 TaskRun 创建前失败，只要 run root 可写，就会写出 pretask incident 与 KnownBugRule candidate。


## TaskRun Continuity v0.4.3

- ProjectGate 可以检测同一个观察到的 goal transcript 中出现多个不同主 TaskRun 路径。
- `projectgate_taskrun_continuity_gate.py` 会在单个 goal 未声明 child run 却切换 TaskRun 时记录 `PG-RUNTIME-SINGLE-PRIMARY-TASKRUN-001`。
- 这用于防止报告、stage gate、delivery check 悄悄绑定到不同于 goal start 的 TaskRun。
