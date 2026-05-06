# AI_Agent_First 项目执行提示词清单

> 用途：基于 [AI_Agent_First_MVP_Architecture.md](C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md) 的方案，为后续在 `AI_Agent_First` 目录中逐步开发项目提供一套可直接复制到 Codex 终端的执行提示词。  
> 原则：优先使用已安装的开发类 skill，并在桌面端 UI 优化阶段配合新增的 4 个设计/截图 skill，把“规划 -> 实现 -> 调试 -> 验收 -> Review”完整串起来。

---

## 1. 使用方式

推荐你以后统一用这个格式下指令：

```text
请使用 <skill名>。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：<当前要做的事>
要求：<输出形式 / 是否改代码 / 是否先出计划 / 是否运行测试>
```

如果任务比较复杂，强烈建议先用 `create-plan`，再进入实现。

---

## 2. 项目初始化阶段

### 2.1 先做开发计划

```text
请使用 create-plan。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：为 AI_Agent_First 单机 MVP 项目生成第一阶段开发计划。
要求：结合架构文档，拆解项目骨架、RAG、自定义 Agent 编排、会话记忆、PyQt6 UI、SQLite 持久化的开发顺序；输出范围、步骤、测试验证和风险点，不要直接修改代码。
```

### 2.2 搭建项目骨架

```text
请先使用 create-plan。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：搭建第一版项目骨架。
要求：计划确认后，创建 app/config、app/rag、app/agent、app/tools、app/services、app/ui、scripts、data 等目录，并生成最小可运行的入口文件与基础配置。
```

### 2.3 生成配置与依赖入口

```text
请使用 test-driven-development。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：实现 settings.py、基础配置加载和项目启动入口。
要求：先为配置加载写失败测试，再实现最小可运行版本；确保后续可以接入 SQLite、Milvus / Milvus Lite 和模型配置，并为后续 Redis 扩展预留接口。
```

---

## 3. RAG 模块开发阶段

### 3.1 实现 Markdown 解析与层级切块

```text
请使用 test-driven-development。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：实现 markdown_parser.py 和 chunker.py，支持基于 Markdown 标题层级的语义切块。
要求：先写失败测试，覆盖标题解析、section_path 保留、长段落二次切块、代码块完整保留等场景；再实现代码并通过测试。
```

### 3.2 实现文档入库脚本

```text
请使用 test-driven-development。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：实现 scripts/ingest_docs.py 和 ingest_pipeline.py。
要求：先写失败测试，验证本地 data/docs 下 Markdown 文档可以被扫描、切块、写入 SQLite 元数据，并预留向量化入 Milvus 的接口。
```

### 3.3 实现检索链路

```text
请使用 test-driven-development。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：实现 retriever.py、vector_store.py、reranker.py、context_builder.py。
要求：先为 retrieve(query) 写失败测试，覆盖向量召回、rerank 精排、上下文组装与来源信息保留；再实现最小可运行版本。
```

### 3.4 调试 RAG 召回效果

```text
请使用 debugging-strategies。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
问题现象：技术问答命中的文档不稳定，答案有偏差。
已知信息：已完成 Markdown 切块、Milvus 检索、Reranker 接入，但部分问题召回不准。
要求：从切块质量、检索参数、metadata 保留、rerank 输入规模、context 组装方式几个角度系统排查，并给出验证步骤。
```

---

## 4. Agent 开发阶段

### 4.1 设计 Agent 状态与节点

```text
请使用 create-plan。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：为当前自定义 Agent 编排设计第一版状态对象和节点交互流程。
要求：结合架构文档中的 AgentState、intent/retrieve/plan/tool/answer/summary 节点，输出精简但可执行的开发计划，不要直接修改代码。
```

### 4.2 实现 Agent Graph

```text
请使用 test-driven-development。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：实现 app/agent/state.py、app/agent/graph.py 以及 intent_node、retrieve_node、plan_node、answer_node 的最小闭环。
要求：先写失败测试，验证用户提问后能够经过 intent -> retrieve -> plan -> answer 完成一次问答流程，再实现代码。
```

### 4.3 实现工具路由与执行

```text
请使用 test-driven-development。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：实现 tool_router_node、tool_exec_node、tools/base.py、tools/registry.py、tools/ops_tools.py。
要求：先写失败测试，覆盖 check_service_status、search_error_logs、restart_mock_service 这 3 个本地模拟工具的注册、路由和执行。
```

### 4.4 实现 Tool Calling 参数校验与自修复

```text
请使用 test-driven-development。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：实现 tools/validators.py，并为工具输入增加 Pydantic 校验和结构化错误反馈。
要求：先写失败测试，覆盖缺字段、类型错误、字段名错误和修复后成功执行的场景；再实现最小自修复闭环。
```

### 4.5 调试 Agent 工具调用不稳定问题

```text
请使用 debugging-strategies。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
问题现象：Agent 能识别需要调用工具，但参数经常生成错误，导致执行失败。
已知信息：已接入本地模拟工具，参数校验器已启用。
要求：按 debugging-strategies 的方法，从 prompt 约束、schema 设计、错误反馈粒度、最大重试次数几个角度排查，并给出修复建议。
```

---

## 5. 会话记忆与持久化阶段

### 5.1 实现会话记忆

```text
请使用 test-driven-development。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：实现 session_service.py，支持 recent messages 与 session summary 的双层记忆。
要求：先写失败测试，覆盖 append_message、recent messages 截断、summary 存取，再实现代码。
```

### 5.2 实现 SQLite 持久化

```text
请使用 test-driven-development。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：实现 sqlite_repo.py，支持 documents、document_chunks、chat_sessions、chat_messages、tool_logs 的初始化和基础读写。
要求：先写失败测试，再实现最小数据库访问层。
```

### 5.3 排查长对话成本问题

```text
请使用 debugging-strategies。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
问题现象：多轮对话后响应变慢，token 消耗过高。
已知信息：recent messages 已接入 SessionService，但摘要压缩策略还不稳定。
要求：从消息保留策略、摘要粒度、context 拼接方式三个角度系统分析，并提出可执行的优化方案。
```

---

## 6. PyQt6 演示端开发阶段

### 6.1 设计 UI 页面结构

```text
请使用 create-plan。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：为 PyQt6 桌面端设计最小演示界面方案。
要求：输出页面结构、控件划分、消息区/来源区/工具日志区的数据流，不要直接改代码。
```

### 6.2 实现主界面和聊天页

```text
请使用 test-driven-development。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：实现 app/ui/main_window.py 和 chat_page.py，完成最小聊天界面。
要求：先写可验证的 UI 行为测试或最小交互测试，再实现输入、发送、展示问答消息的最小功能。
```

### 6.3 实现来源卡片和工具日志面板

```text
请使用 test-driven-development。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：实现 source_card.py 和 tool_log_panel.py。
要求：让 UI 能展示命中文档来源、章节路径、工具调用状态和执行结果，优先保证演示效果清晰。
```

### 6.4 排查 PyQt6 卡顿问题

```text
请使用 debugging-strategies。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
问题现象：发送问题后 UI 会卡住，工具执行期间界面无响应。
已知信息：LLM 调用、检索和工具执行目前可能运行在主线程。
要求：排查线程模型、signal/slot 使用、后台任务分发方式，并给出修复方案。
```

### 6.5 使用桌面端 UI / 设计辅助 Skill

这 4 个 skill 适合在 Codex 桌面端 Windows 环境下配合当前 PyQt 项目使用：

- `figma-create-design-system-rules`：先沉淀当前项目的桌面端设计规则，统一字体、间距、色彩、圆角、卡片层级和状态色。
- `figma-generate-design`：基于已有页面结构，生成更完整的桌面端界面方案或局部改版方案。
- `figma-implement-design`：把 Figma 中确认过的界面方案转成项目里的实际 UI 代码。
- `screenshot`：对当前客户端界面做验收截图，检查布局抖动、滚动区溢出、面板对齐和消息渲染效果。

推荐调用顺序：

1. 先用 `figma-create-design-system-rules` 固定桌面端风格规则。
2. 再用 `figma-generate-design` 生成页面或局部模块方案。
3. 方案确认后，用 `figma-implement-design` 落到 PyQt 界面实现。
4. 每次较大改动后，用 `screenshot` 做前后对比验收。

使用规范：

- 优先服务当前桌面端 PyQt 客户端，不要把重点偏到 Web 或移动端。
- 先解决窗口尺寸抖动、长回答导致布局变化、消息区滚动体验，再做装饰性美化。
- 优先优化聊天主区、来源区、工具日志区、会话摘要区和遥测信息区的可读性。
- 没有明确收益时，不额外引入图片化素材，优先使用代码可维护的配色、字体、边框和布局方案。
- 每次 UI 大改前后都建议保留截图，重点观察窗口是否跳变、控件是否被挤压、流式输出时是否稳定。

可直接复制的提示词模板如下。

#### 6.5.1 先建立桌面端设计规则

```text
请使用 figma-create-design-system-rules。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：为当前 AI_Agent_First 桌面端客户端生成一套可执行的设计系统规则。
要求：面向 Codex Desktop Windows + PyQt 聊天客户端；重点约束字体层级、消息气泡、侧栏、卡片、按钮、日志面板、状态标签、遥测信息和颜色变量；优先保证长回答场景下布局稳定，不直接修改业务代码。
```

#### 6.5.2 生成桌面端界面方案

```text
请使用 figma-generate-design。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：为当前桌面端客户端生成一版更完整的 UI 方案。
要求：保留消息区、来源区、工具日志区、会话摘要区、输入区和状态栏；突出 SSE 流式输出、首包延迟、总耗时和 provider 诊断信息的展示；界面偏桌面工作台风格，不要做成移动端卡片流。
```

#### 6.5.3 把设计方案落成代码

```text
请使用 figma-implement-design。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：根据确认后的 Figma 方案优化当前 PyQt 客户端界面实现。
要求：尽量复用现有窗口结构与组件职责，不重写无关模块；重点修正布局抖动、空间分配、状态信息展示和消息可读性；改完后说明具体修改点与验证方式。
```

#### 6.5.4 用截图进行界面验收

```text
请使用 screenshot。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：对当前桌面端客户端做界面验收截图并给出问题清单。
要求：重点检查窗口尺寸是否随回答变化、消息区是否溢出、面板是否对齐、滚动是否自然、遥测区和工具日志区是否清晰；输出截图观察结论和下一步修正建议，不改业务逻辑。
```

---

## 7. 代码审查与质量保障阶段

### 7.1 对当前 diff 做整体审查

```text
请使用 review-swarm。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：审查当前 git diff。
要求：重点检查 RAG 链路是否有行为回归、Agent 状态流是否稳定、工具调用是否有参数风险、Redis/SQLite 是否存在数据一致性问题，不要改代码。
```

### 7.2 对指定模块做专项审查

```text
请使用 review-swarm。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：审查这些文件：app/rag/chunker.py, app/rag/retriever.py, app/agent/graph.py, app/tools/validators.py。
要求：重点关注检索准确率风险、Agent 节点顺序问题、参数自修复是否可能死循环、测试覆盖是否足够，不要改代码。
```

---

## 8. GitHub 协作阶段

### 8.1 查看并处理 PR 评论

```text
请使用 gh-address-comments。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
任务：拉取当前分支对应 PR 的所有 review comments，按编号总结每条评论需要修改什么，然后等我选择要处理哪些。
要求：先不要改代码。
```

### 8.2 修复 PR 评论中选中的问题

```text
请使用 gh-address-comments。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
任务：处理我选中的 PR 评论，并在修改后总结改动内容、影响范围和已完成验证。
```

### 8.3 分析 GitHub Actions 失败原因

```text
请使用 gh-fix-ci。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
任务：查看当前分支对应 PR 的 GitHub Actions 失败项，总结失败原因并给出修复计划。
要求：先不要直接改代码，先输出失败检查项、关键日志和修复步骤。
```

### 8.4 修复 CI 问题后再做审查

```text
请先使用 gh-fix-ci。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
任务：分析当前 PR 的 CI 失败原因并给出修复计划；如果确认是代码问题，修复后再使用 review-swarm 审查本次改动。
要求：重点关注测试、依赖、配置和路径问题。
```

---

## 9. 按阶段推进的推荐顺序

| 阶段 | 推荐先用的 skill | 目标 |
|---|---|---|
| 项目立项 | `create-plan` | 先把范围和开发顺序拆清楚 |
| 模块实现 | `test-driven-development` | 保证每个核心模块先有失败测试再写实现 |
| 效果排查 | `debugging-strategies` | 系统定位召回差、参数错误、卡顿等问题 |
| 合并前审查 | `review-swarm` | 从回归、安全、可靠性、测试覆盖角度把关 |
| PR 协作 | `gh-address-comments` | 批量处理 review comments |
| CI 故障 | `gh-fix-ci` | 识别并修复 GitHub Actions 失败项 |

---

## 10. 最短常用模板

### 10.1 先做计划

```text
请使用 create-plan。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：为当前开发任务先做计划，不要直接改代码。
```

### 10.2 按 TDD 实现

```text
请使用 test-driven-development。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
任务：实现当前模块。
要求：先写失败测试，再写最小实现，最后验证通过。
```

### 10.3 排查问题

```text
请使用 debugging-strategies。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
参考文档：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First\AI_Agent_First_MVP_Architecture.md
问题现象：<填写问题>
已知信息：<填写上下文>
要求：系统排查并给出验证步骤。
```

### 10.4 合并前审查

```text
请使用 review-swarm。
项目目录：C:\Users\JXW\Documents\Codex\2026-04-22-codex-skills-github-skills\AI_Agent_First
任务：审查当前 diff。
要求：只输出高价值问题，不要改代码。
```

---

## 11. 推荐的实际开发节奏

可以按下面这条节奏推进：

1. 先用 `create-plan` 明确当前阶段目标
2. 再用 `test-driven-development` 实现一个最小模块
3. 如果效果不稳，用 `debugging-strategies` 排查
4. 每完成一个阶段，用 `review-swarm` 做一次质量审查
5. 有 PR 后，用 `gh-address-comments` 和 `gh-fix-ci` 处理协作问题

最适合这个项目的路径是：

**create-plan -> test-driven-development -> debugging-strategies -> review-swarm -> gh-address-comments / gh-fix-ci**

---

## 12. 一句话总结

这份提示词清单的目标，不是让 Codex 零散地帮你“写几段代码”，而是把 `AI_Agent_First` 这个项目真正按工程化节奏推进下去：

**先规划，再测试驱动实现；遇到问题系统排查；提交前做审查；进入 GitHub 协作后处理评论与 CI。**
