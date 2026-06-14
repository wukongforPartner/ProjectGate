# Knowledge Lifecycle v0.1

## SOP 生命周期

```text
SOP_CANDIDATE -> owner review -> ACTIVE_SOP -> matching tasks loaded
```

## Incident 生命周期

```text
INCIDENT -> known bug rule candidate -> owner review -> ACTIVE_KNOWN_BUG_RULE -> gate check
```

## 未知任务类型

如果没有匹配的任务类型或 SOP，进入只读发现阶段，并生成候选任务类型和候选 SOP。
