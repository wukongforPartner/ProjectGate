# ProjectGate Alpha 快速开始

本文面向第一次使用 ProjectGate 的用户。

## ProjectGate 是什么

ProjectGate 会把你的项目文档、SOP、规则和事故记录编译成 AI 工作流层。

目标：

```text
你提供项目文档。
ProjectGate 生成 Project Pack。
Codex 使用 $projectgate 和 L/M/H 档位工作。
AI 不再临场发挥，而是按事实、阶段、报告和 owner decision 工作。
```

## 环境要求

- Python 3
- 如果要接 Codex，需要已经安装并登录 Codex
- 一个项目目录
- 一个包含项目文档 / SOP / 规则 / 事故记录的文件夹

## 第 1 步：解压

例如：

```powershell
D:\ProjectGate_Alpha_v0_1_1
```

进入目录：

```powershell
cd "D:\ProjectGate_Alpha_v0_1_1"
```

## 第 2 步：本地自测

```powershell
python ".\scripts\alpha_selftest.py"
```

期望：

```text
RESULT=PASS
ALPHA_SELFTEST=PASS
```

## 第 3 步：初始化工作区

你可以自己选择路径。

```powershell
python ".\install_projectgate_alpha.py" --dry-run --workspace-root "D:\ProjectGate"
python ".\install_projectgate_alpha.py" --install --workspace-root "D:\ProjectGate"
```

## 第 4 步：准备项目文档

创建类似目录：

```text
D:\MyProjectDocs\
  project_overview.md
  rules.md
  sop.md
  known_incidents.md
```

可以复制模板：

```text
examples\ProjectDocsInbox_Template\
```

## 第 5 步：编译 Project Pack

```powershell
python ".\install_projectgate_alpha.py" --install `
  --workspace-root "D:\ProjectGate" `
  --project-name "MyProject" `
  --project-root "D:\MyProject" `
  --docs-dir "D:\MyProjectDocs" `
  --build-pack
```

输出：

```text
D:\ProjectGate\ProjectPacks\MyProject\
```

## 第 6 步：构建并安装 Codex Skill

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

安装位置：

```text
%USERPROFILE%\.agents\skills\projectgate
```

默认不会安装项目 `AGENTS.md`。

## 第 7 步：在 Codex 中使用

从项目根启动 Codex：

```powershell
cd "D:\MyProject"
codex
```

先使用低消耗档：

```text
/goal $projectgate -p L: Review this issue and produce an action queue. Do not modify project files.
```

档位：

```text
-p L = low / light
-p M = medium / standard
-p H = high / deep
```

## 可选：安装项目 AGENTS.md

这一步会写入项目根目录。没有准备好之前不要做。

## 安全模型

ProjectGate Alpha 默认：

- 先只读
- 不猜
- 需要判断或写操作时停下等 owner
- 只有明确授权才写项目文件
- 可复用流程变成 SOP candidate
- 可复现错误变成 KnownBugRule candidate

## 当前限制

- 当前原生适配器优先支持 Codex。
- Generic Markdown 支持还比较基础。
- hooks 默认没有完整安装。
- SOP 和 KnownBugRule candidate 仍需 owner 审核才能激活。

## ProjectGate Runtime v0.2

Alpha v0.2.0 新增 Runtime Gate：SOP 和 KnownBugRules 不再只是文档结构。真实工作流必须先生成 `TaskRun.json`，把 active SOP / KnownBugRules 载入本次任务；阶段输出必须通过 stage gate；失败时进入 `REPAIR_AND_RECHECK`，修正后重新检查；最终交付前必须通过 delivery check。

## ProjectGate Knowledge Router v0.3

Alpha v0.3.0 新增知识路由与沉淀闭环：`L / M / H` 不再只是成本标签，也决定 SOP / KnownBugRule 的选择范围。成功且可复用的 TaskRun 可以生成 SOP candidate；失败事故可以生成 KnownBugRule candidate；candidate 必须 owner 批准后才进入 active。

## ProjectGate Auto Capture v0.4.0

Alpha v0.4.0 新增自动沉淀闭环：stage gate / delivery check 失败会自动生成 incident 和 KnownBugRule candidate；delivery check 成功会自动生成 SOP candidate。owner 只负责 approve / reject，不再负责手写候选规则。若已有同类规则，系统会记录是 active 规则未被选中、已选中但未执行、还是规则粒度不够。
