# ProjectGate 背景与问题说明

## 背景

现在越来越多人开始把 AI 用进真实项目里：写代码、改文档、查问题、做数据分析、整理需求、生成脚本、辅助发版。

但一旦项目变复杂，问题很快就会暴露出来。

AI 单次回答可以很强，但长期协作并不稳定。它可能在上一句话里承诺“只读审查”，下一步就开始给补丁；它可能把猜测写成事实；它可能在缺少当前现场的情况下继续推进；它可能重复犯已经被纠正过的错误；它可能忘记项目里已有的 SOP、门禁、事故沉淀和团队规则。

这不是某一个模型的问题，而是 AI 进入长期项目协作时的结构性问题：

**项目规则是文档，AI 的行为是即时生成。两者之间缺少一层可执行的工作流。**

人类团队可以靠流程、分工、审批、复盘、SOP、事故记录来减少错误。但大多数 AI 协作仍停留在“把规则写进提示词，然后希望它记住”的阶段。这在简单任务里可行，在复杂项目里会反复失效。

ProjectGate 就是为了解决这个问题而产生的。

---

## ProjectGate 要解决的问题

ProjectGate 解决的不是“让 AI 更聪明”这个问题。

它解决的是：

**如何让 AI 在真实项目中按事实、阶段、角色、门禁和项目知识工作。**

它针对的是这些常见失控点：

1. **缺事实推进**  
   AI 没有当前代码、配置、运行状态，却直接给结论、方案或补丁。

2. **把猜测写成事实**  
   AI 用“我认为”“通常来说”“大概率”替代真实证据。

3. **越阶段行动**  
   本该只读审查，却直接进入设计、字段、补丁、命令、发版。

4. **自己审自己**  
   生成方案的同一个模型又批准方案，缺少反证角色和确定性 gate。

5. **重复犯错**  
   某次事故被总结过，但下次同类任务 AI 仍然从零开始，甚至重犯旧错。

6. **项目文档无法真正生效**  
   团队有大量 SOP、规范、门禁、事故记录，但 AI 不一定加载，不一定理解，也不一定执行。

7. **上下文和额度浪费**  
   模型直接阅读整个项目、整个仓库或大量日志，成本高，效率低，也容易迷失重点。

8. **用户变成人肉调度器**  
   AI 每一步都需要用户提醒“继续”“别补丁”“先查事实”“写报告”，协作没有真正自动化。

ProjectGate 的目标是把这些问题从“靠模型自觉”改成“靠工作流和门禁约束”。

---

## ProjectGate 是什么

ProjectGate 是一个面向 AI 协作的项目治理层。

它不是一个新的大模型，也不是一个普通提示词模板。它是一套把项目知识编译成 AI 工作流的结构。

它包含：

- **Core**：通用治理规则，例如不猜、缺事实停、阶段门禁、多角色校验、Owner Decision、SOP 生命周期、事故沉淀。
- **Project Pack**：某个具体项目的规则、SOP、KnownBugRules、任务类型、证据收集方式。
- **Adapter**：把 Core + Project Pack 转成某个 AI 工具能使用的格式，例如 Codex Skill、AGENTS.md、Markdown Runbook。
- **KnowledgeBase**：保存项目中的 SOP、事故、KnownBugRules、TaskTypes，并支持候选到激活的流程。
- **Evidence / CodeMap 工具**：先用本地脚本收集压缩事实，再让模型判断，减少上下文浪费。
- **Owner Decision 协议**：当需要产品判断、风险接受或写操作授权时，AI 必须停下来给用户选项，而不是自作主张。

一句话说：

**ProjectGate 把“项目文档”变成“AI 可以执行的项目工作流”。**

---

## 它和普通提示词有什么不同

普通提示词是：

> 请你遵守这些规则。

ProjectGate 是：

> 任务必须经过这些阶段；  
> 缺少事实就停；  
> 某些动作没有授权不能执行；  
> 旧错误会变成规则；  
> 成功流程会变成 SOP；  
> 不同角色负责事实、审查、反证、验证；  
> 完整报告写入文件；  
> 用户只在必须判断时介入。

也就是说，ProjectGate 不只是告诉 AI “应该怎么做”，而是把“怎么做”拆成可执行的结构：

```text
文档
  -> 结构化 Project Pack
  -> 阶段工作流
  -> 事实包
  -> 多角色校验
  -> 门禁检查
  -> 报告
  -> Owner Decision
  -> SOP / Incident 沉淀
```

---

## 它不是训练模型，而是编译项目知识

ProjectGate 的一个核心思想是：

**不是训练模型，而是编译项目知识。**

每个项目本来就有大量知识：项目说明、技术栈、代码结构、开发规范、测试流程、发版规则、常见事故、团队协作习惯、禁止事项、已验证 SOP。

这些东西通常散落在 README、文档、聊天记录、交接文件和人的脑子里。

ProjectGate 的做法是把它们整理成结构化资产：

```text
ProjectDocs
  -> AGENTS.md
  -> Project Pack
  -> SOP candidates
  -> KnownBugRule candidates
  -> Evidence profiles
  -> AI tool adapter package
```

这样 AI 不再每次从零理解项目，而是进入一个已经有轨道、有信号灯、有事故记录、有操作规程的工作环境。

---

## 为什么需要多角色校验

复杂项目中，单个 AI 角色很容易出现“自己说服自己”的问题。

ProjectGate 使用角色分离：

- **FactCollector**：只收集事实，不给方案。
- **Synthesizer**：整理事实和选项。
- **AdversaryReviewer**：专门找缺事实、矛盾和越界。
- **Gatekeeper**：执行确定性检查，不能由提案者自己担任。
- **Executor**：只执行已授权动作。
- **Verifier**：独立验证执行结果。
- **KnowledgeCurator**：把成功流程和失败事故沉淀成候选知识。
- **Owner**：做价值判断和授权。

这套结构的目的不是让 AI 看起来更复杂，而是避免一个核心问题：

**生成答案的人不能成为批准答案的人。**

---

## 为什么需要 Owner Decision

AI 可以帮用户推进事实工作，但不能替用户做价值判断。

例如：是否接受某个产品方向、是否允许修改项目文件、是否允许发版、是否接受某个风险、是否把某条候选 SOP 永久激活。

这些不是模型应该擅自决定的事情。

ProjectGate 使用固定格式：

```text
OWNER_DECISION_REQUIRED

问题：
...

选项：
A. ...
B. ...
C. ...

推荐：
A

推荐理由：
...

你可以回复 A / B / C，或直接输入你的判断。
```

这样用户不需要一直当流程调度员，只需要在真正需要判断时介入。

---

## 为什么需要 SOP 和事故沉淀

很多 AI 协作失败不是因为第一次犯错，而是因为反复犯同类错误。

ProjectGate 把成功和失败都转成可复用知识。

成功流程：

```text
完成一次正确流程
  -> SOP_CANDIDATE
  -> owner 审查
  -> ACTIVE_SOP
  -> 下次同类任务自动加载
```

失败事故：

```text
发生一次可复现错误
  -> INCIDENT
  -> KnownBugRuleCandidate
  -> owner 审查
  -> ACTIVE_KNOWN_BUG_RULE
  -> 下次同类任务强制检查
```

这让项目经验不再只停留在“下次注意”，而是进入下次工作流。

---

## ProjectGate 能用于哪些项目

ProjectGate 最初来自一个复杂独立游戏项目的真实协作需求，但它抽象出来的问题并不局限于游戏。

它适合所有具有这些特征的长期项目：

- 项目文档多
- SOP 多
- 规则多
- 事故教训多
- AI 参与深
- 任务有阶段和风险
- 需要长期复用经验
- 不能接受 AI 随意猜测或越权行动

典型场景包括：软件工程、游戏开发、后端 / DevOps、数据分析、内容生产、研究项目、法律 / 合规文档审查、产品设计、开源项目维护。

---

## 一个典型使用流程

用户准备项目文档：

```text
ProjectDocsInbox/
  project_overview.md
  rules.md
  sop.md
  known_incidents.md
  release_rules.md
```

运行 ProjectGate：

```text
ProjectGate compile
```

生成 Project Pack：

```text
ProjectPack/
  AGENTS.md.template
  README_ProjectPack.md
  SOPs/
  KnownBugRules/
  TaskTypes/
  EvidenceProfiles/
```

安装到 AI 工具，例如 Codex：

```text
ProjectGate Adapter -> Codex Skill
```

日常使用：

```text
/goal $projectgate -p L: Review this issue and produce an action queue. Do not modify project files.
```

AI 会按项目规则推进到可交付报告、可执行队列、Owner Decision、缺事实阻塞或写操作授权点。

---

## ProjectGate 的核心价值

ProjectGate 的价值不是“让 AI 回答更多”。

它的价值是：

**让 AI 少乱做、少重犯、少猜测、少浪费，并把项目经验变成可复用流程。**

它把 AI 协作从“提示词驱动”推进到“项目工作流驱动”。

这意味着 AI 不再只是一个随时可能忘记规则的聊天对象，而是被放进一个有项目纪律、有事实约束、有复盘沉淀、有授权边界的协作系统里。

---

## 当前阶段

ProjectGate 目前处于 Alpha 阶段。

已经实现的方向包括：

- Core / Project Pack 拆分
- Codex Adapter
- 文档模板
- Project Pack 编译
- Codex Skill 生成
- L / M / H 工作档位
- 基础 SOP / Incident / KnownBugRule 结构
- 安装和自测脚本

仍在完善的方向包括：

- 更完整的 hard hooks
- 更强的 CodeGraph / tree-sitter / MCP 工具层
- 更多 AI 工具 Adapter
- SOP promotion 的图形化或半自动审查流程
- KnownBugRule 的更强机器校验
- 更低成本的 smoke test 策略

---

## 一句话总结

ProjectGate 是一个把项目文档、SOP、门禁和事故经验编译成 AI 工作流的治理层。

它的目标不是替代人，而是让 AI 在长期复杂项目中按事实、流程、角色和授权边界工作。

## ProjectGate Runtime v0.2

Alpha v0.2.0 新增 Runtime Gate：SOP 和 KnownBugRules 不再只是文档结构。真实工作流必须先生成 `TaskRun.json`，把 active SOP / KnownBugRules 载入本次任务；阶段输出必须通过 stage gate；失败时进入 `REPAIR_AND_RECHECK`，修正后重新检查；最终交付前必须通过 delivery check。

## ProjectGate Knowledge Router v0.3

Alpha v0.3.0 新增知识路由与沉淀闭环：`L / M / H` 不再只是成本标签，也决定 SOP / KnownBugRule 的选择范围。成功且可复用的 TaskRun 可以生成 SOP candidate；失败事故可以生成 KnownBugRule candidate；candidate 必须 owner 批准后才进入 active。

## ProjectGate Auto Capture v0.3.1

Alpha v0.3.1 新增自动沉淀闭环：stage gate / delivery check 失败会自动生成 incident 和 KnownBugRule candidate；delivery check 成功会自动生成 SOP candidate。owner 只负责 approve / reject，不再负责手写候选规则。若已有同类规则，系统会记录是 active 规则未被选中、已选中但未执行、还是规则粒度不够。
