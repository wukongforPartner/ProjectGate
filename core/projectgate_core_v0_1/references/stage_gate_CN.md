# Stage Gate v0.1

## 阶段

- INTAKE
- READONLY_AUDIT
- FACT_COLLECTION
- ENTRY_MAP
- ANCHOR_MAP
- PLAN
- WRITE_AUTHORIZATION
- EXECUTION
- VERIFICATION
- HANDOFF

## 规则

工作流只能执行当前阶段允许的动作。如果任务需要进入后续阶段，必须停止并请求 owner 授权。
