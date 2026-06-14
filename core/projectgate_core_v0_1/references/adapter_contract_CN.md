# Adapter Contract v0.1

Adapter 会把 ProjectGate assets 转成某个 AI 工具的原生配置格式。

## 输入

- Project Pack
- Core references
- Active SOPs
- Active KnownBugRules
- Tool constraints

## 输出示例

- 项目指令文件
- Skill 或 workflow 包
- Hook 模板
- Rules 文件
- 通用 prompt 包

## 规则

Adapter 不得静默丢弃硬门禁。不支持的门禁必须报告为 `UNSUPPORTED_GATE`。
