# 企业级智能运维与研发知识自动化平台

## 单机最小落地版架构与实现方案

> 目标：先实现一个单机可运行、可演示、可写入简历的 MVP 版本。  
> 当前实现技术栈：`Python + 自定义 Agent 编排 + RAG + PyQt6 + SQLite + OpenAI-Compatible LLM + Milvus Lite/Milvus`
> 当前仓库的会话链路由 `SessionService + SQLite summary` 承担，`LangGraph/LangChain/Redis` 仍可作为后续增强方向。

---

## 1. 项目定位

这个项目的最小落地版本，不追求一开始就覆盖企业级全部能力，而是优先完成一条可以真实演示的闭环：

1. 导入本地技术文档
2. 建立向量索引
3. 实现技术问答
4. 基于 Agent 调用本地模拟工具完成运维动作
5. 保存会话上下文
6. 在 PyQt6 桌面端可视化展示

这个版本的核心价值不是“大而全”，而是：

- 能跑通 RAG 问答
- 能展示 Agent 自动化流程
- 能体现长对话优化思路
- 能支撑后续扩展成企业级平台

---

## 2. 单机 MVP 总体架构

```mermaid
flowchart TD
    A["PyQt6 桌面端"] --> B["应用服务层"]
    B --> C["自定义 Agent 编排"]
    B --> D["RAG 检索服务"]
    B --> E["会话记忆服务"]
    B --> F["SQLite 元数据"]

    D --> G["Markdown 文档解析"]
    G --> H["语义分段 Chunker"]
    H --> I["Embedding 向量化"]
    I --> J["Milvus 向量检索"]
    J --> K["BGE Reranker 精排"]
    K --> L["Context Builder"]
    L --> M["LLM 生成答案"]

    C --> N["意图识别"]
    N --> O["检索节点"]
    O --> P["规划节点"]
    P --> Q["工具路由节点"]
    Q --> R["工具执行节点"]
    R --> S["观察/反馈节点"]
    S --> P
    P --> T["最终回答节点"]

    Q --> U["本地运维工具模拟器"]
    U --> V["执行结果"]
    V --> T
```

---

## 3. 单机 MVP 的设计边界

### 3.1 In Scope

- 本地 Markdown 技术文档导入
- Milvus 向量检索
- BGE-Reranker 精排
- 自定义多节点 Agent 编排
- 本地模拟运维工具调用
- recent messages + summary 会话记忆
- PyQt6 桌面演示界面
- SQLite 持久化会话与文档元数据

### 3.2 Out of Scope

- 企业统一登录
- 真实生产环境高危命令执行
- 多租户权限系统
- 集群化部署
- 海量并发处理
- 完整审批流

---

## 4. 为什么先做单机版

| 目标 | 单机版价值 |
|---|---|
| 简历项目可讲清楚 | 可以完整展示从知识检索到 Agent 自动化闭环 |
| 开发复杂度可控 | 先解决核心链路，不被分布式和权限系统拖住 |
| 便于演示 | 本地就能演示导入文档、提问、检索、调用工具 |
| 容易逐步升级 | 后续可平滑替换 SQLite、工具执行层、鉴权层 |

---

## 5. 推荐项目目录结构

```text
AI_Agent_First/
  app/
    main.py
    config/
      settings.py
      logging.py
    core/
      constants.py
      exceptions.py
    models/
      document.py
      message.py
      session.py
      tool_result.py
    rag/
      markdown_parser.py
      chunker.py
      embedding_service.py
      vector_store.py
      reranker.py
      retriever.py
      context_builder.py
      ingest_pipeline.py
    agent/
      graph.py
      state.py
      prompts.py
      nodes/
        intent_node.py
        retrieve_node.py
        plan_node.py
        tool_router_node.py
        tool_exec_node.py
        answer_node.py
        summary_node.py
    tools/
      base.py
      registry.py
      ops_tools.py
      validators.py
    services/
      llm_service.py
      session_service.py
      summary_service.py
      document_service.py
    repositories/
      sqlite_repo.py
    ui/
      main_window.py
      pages/
        chat_page.py
        docs_page.py
        logs_page.py
      widgets/
        message_bubble.py
        source_card.py
        tool_log_panel.py
  data/
    docs/
    cache/
    sqlite/
  scripts/
    ingest_docs.py
    run_demo.py
  README.md
```

---

## 6. 核心模块拆解

### 6.1 文档接入模块

职责：

- 扫描本地 Markdown 文档
- 提取标题层级
- 基于语义切块
- 写入 Milvus
- 保存元数据到 SQLite

建议输入目录：

```text
data/docs/
  redis/
  mysql/
  kubernetes/
  incidents/
```

### 6.2 RAG 检索模块

职责：

- 对用户问题做预处理
- 向量召回
- reranker 精排
- 上下文组装
- 返回可被 LLM 消费的高质量 context

### 6.3 Agent 编排模块

职责：

- 判断用户是在问知识、要排障，还是要执行操作
- 决定是否进入工具调用
- 将检索结果和工具结果融合
- 输出最终回答

### 6.4 会话记忆模块

职责：

- SessionService 保存最近若干轮消息
- 保存会话摘要
- 降低长对话 token 成本

### 6.5 PyQt6 演示界面

职责：

- 输入问题
- 展示回答
- 展示引用来源
- 展示工具执行过程
- 切换会话

### 6.6 Codex 桌面端 UI 设计辅助 Skill 规范

为了让当前 MVP 在 Codex 桌面端 Windows 环境下更高效地完成 UI 迭代，可以把新增的 4 个 skill 纳入桌面端开发闭环。它们不替代 PyQt 代码实现本身，而是作为“规则制定 -> 方案生成 -> 代码落地 -> 截图验收”的辅助工具。

对应关系如下：

- `figma-create-design-system-rules`：用于沉淀当前项目的桌面端设计规则，统一聊天窗口、侧栏、按钮、面板、状态标签和信息层级。
- `figma-generate-design`：用于生成或重构桌面端页面方案，适合在现有产品结构上做可视化整理与体验增强。
- `figma-implement-design`：用于把已确认的 Figma 方案转成项目中的实际 UI 代码实现。
- `screenshot`：用于真实界面验收，观察流式输出、长回答、日志展开、来源卡片和状态栏在运行过程中的稳定性。

推荐工作流：

1. 先定义桌面端设计规则，避免后续多次返工。
2. 再生成聊天页、日志区、来源区、状态栏等关键区域的整体方案。
3. 方案确认后落到 PyQt 代码中，保持现有业务链路不被破坏。
4. 用截图做验收，记录窗口抖动、溢出、对齐和滚动问题，再进行下一轮修正。

使用边界与规范：

- 明确以桌面端客户端为中心，不为 Web 或移动端额外设计复杂适配层。
- 优先保证 SSE 流式输出、长回答渲染、会话摘要展示、provider 诊断区和遥测区的稳定可读。
- 优先修复窗口大小变化、控件挤压、消息区回流和滚动异常，再做视觉层的润色。
- 能用样式、布局和组件层级解决的问题，尽量不要引入额外图片资源，减少后续维护成本。
- 截图验收时，应重点观察消息区、来源区、工具日志区、摘要区、状态栏和输入区之间的空间分配是否稳定。

---

## 7. 数据流说明

### 7.1 文档入库流程

```mermaid
flowchart LR
    A["读取 Markdown 文档"] --> B["解析标题结构"]
    B --> C["按层级切块"]
    C --> D["生成 Embedding"]
    D --> E["写入 Milvus"]
    C --> F["保存 Chunk 元数据到 SQLite"]
```

### 7.2 用户问答流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant UI as PyQt6
    participant AG as Agent
    participant RAG as RAG服务
    participant VS as Milvus
    participant RR as Reranker
    participant LLM as 大模型
    participant RE as SessionService / SQLite

    U->>UI: 提问
    UI->>AG: 发送输入
    AG->>RAG: 请求检索
    RAG->>VS: 向量召回
    VS-->>RAG: 候选文档
    RAG->>RR: 精排
    RR-->>RAG: Top文档
    RAG-->>AG: 上下文
    AG->>LLM: 生成回答
    LLM-->>AG: 回答
    AG->>RE: 更新会话状态
    AG-->>UI: 返回答案+来源
```

### 7.3 Agent 工具执行流程

```mermaid
flowchart TD
    A["用户请求: 重启 Redis 服务"] --> B["Intent Node"]
    B --> C["Plan Node"]
    C --> D["Tool Router"]
    D --> E["参数校验"]
    E -->|通过| F["本地工具执行"]
    E -->|失败| G["反馈修复 Prompt"]
    G --> D
    F --> H["Observation Node"]
    H --> I["Answer Node"]
```

---

## 8. 单机 MVP 的功能优先级

| 优先级 | 功能 | 说明 |
|---|---|---|
| P0 | Markdown 文档导入 | 没有知识库，RAG 无法工作 |
| P0 | Milvus 检索 + Rerank | 决定问答质量 |
| P0 | Agent 编排基础链路 | 决定是否能展示自动化链路 |
| P0 | PyQt6 聊天主界面 | 决定是否能完整演示 |
| P1 | recent messages + summary 会话记忆 | 支撑多轮对话和成本优化 |
| P1 | 本地模拟运维工具 | 用于演示 Tool Calling 与 ReAct |
| P2 | 摘要压缩 | 用于体现长对话优化亮点 |
| P2 | 引用来源高亮 | 增强演示效果和可信度 |

---

## 9. 本地最小实现建议

### 9.1 文档源

先只接 Markdown，原因：

- 易解析
- 能保留标题层级
- 适合做层级切块
- 容易构造演示数据

### 9.2 工具执行层

先不要直接接真实生产 API，建议做本地模拟工具：

- `check_service_status`
- `search_error_logs`
- `restart_mock_service`
- `get_incident_summary`

这样既能展示 Agent 自动化能力，又避免高风险。

### 9.3 数据存储

| 数据类型 | 技术 |
|---|---|
| 向量数据 | Milvus |
| 会话状态 | SessionService（内存） + SQLite Summary |
| 文档元数据/聊天记录 | SQLite |

---

## 10. 核心数据模型

### 10.1 Chunk 模型

```python
from pydantic import BaseModel
from typing import List


class DocumentChunk(BaseModel):
    doc_id: str
    chunk_id: str
    title: str
    section_path: List[str]
    content: str
    source: str
    tags: List[str] = []
    order: int
    token_count: int
```

### 10.2 Agent State

```python
from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict, total=False):
    session_id: str
    user_query: str
    rewritten_query: str
    intent: str
    retrieved_docs: List[Dict[str, Any]]
    context_text: str
    selected_tool: str
    tool_input: Dict[str, Any]
    tool_output: Dict[str, Any]
    observations: List[str]
    final_answer: str
    summary: str
    retry_count: int
    error: str
```

### 10.3 Tool Result

```python
from pydantic import BaseModel
from typing import Any


class ToolResult(BaseModel):
    success: bool
    code: str
    message: str
    data: Any = None
    retryable: bool = False
```

---

## 11. Markdown 层级切块实现建议

目标：解决长文档切块后语义断裂问题。

策略：

1. 先按 `# / ## / ###` 建立章节树
2. 每块保留父级标题路径
3. 每个 chunk 控制在 300 到 600 tokens
4. 对超长段落二次切块
5. 代码块和命令块整体保留
6. 相邻 chunk 保留 50 到 80 tokens overlap

### 核心代码示例

```python
import re
from dataclasses import dataclass, field


@dataclass
class Section:
    title: str
    level: int
    content: list[str] = field(default_factory=list)
    path: list[str] = field(default_factory=list)


def split_markdown_sections(text: str) -> list[Section]:
    sections: list[Section] = []
    current = Section(title="ROOT", level=0, path=[])

    for line in text.splitlines():
        match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if match:
            if current.content:
                sections.append(current)
            level = len(match.group(1))
            title = match.group(2).strip()
            path = current.path[: level - 1] + [title]
            current = Section(title=title, level=level, path=path, content=[])
        else:
            current.content.append(line)

    if current.content:
        sections.append(current)

    return sections
```

---

## 12. RAG 检索链路设计

### 12.1 检索链路

```mermaid
flowchart LR
    A["用户问题"] --> B["Query 预处理"]
    B --> C["Milvus 向量召回 TopK"]
    C --> D["BGE Reranker 精排"]
    D --> E["Context Builder"]
    E --> F["LLM 生成答案"]
```

### 12.2 检索参数建议

| 参数 | 建议值 |
|---|---|
| 向量召回 top_k | 15 到 20 |
| rerank 输入数 | 10 到 15 |
| 最终上下文块数 | 4 到 6 |
| chunk 大小 | 300 到 600 tokens |
| overlap | 50 到 80 tokens |

### 12.3 检索伪代码

```python
def retrieve(query: str):
    rewritten = rewrite_query(query)
    candidates = milvus_search(rewritten, top_k=20)
    ranked = rerank(query, candidates)
    top_docs = ranked[:5]
    context = build_context(top_docs)
    return context, top_docs
```

---

## 13. Agent 编排设计

### 13.1 节点划分

| 节点 | 作用 |
|---|---|
| `intent_node` | 判断用户问题属于问答、排障还是执行 |
| `retrieve_node` | 执行 RAG 检索 |
| `plan_node` | 规划下一步行为 |
| `tool_router_node` | 判断是否需要调用工具 |
| `tool_exec_node` | 执行工具 |
| `answer_node` | 生成最终答案 |
| `summary_node` | 更新会话摘要 |

### 13.2 Graph 代码骨架

```python
from dataclasses import dataclass


def run_agent(state: AgentState):
    state = intent_node(state)
    state = retrieve_node(state)
    state = plan_node(state)
    graph.add_node("tool_router", tool_router_node)
    graph.add_node("tool_exec", tool_exec_node)
    graph.add_node("answer", answer_node)
    graph.add_node("summary", summary_node)

    graph.set_entry_point("intent")
    graph.add_edge("intent", "retrieve")
    graph.add_edge("retrieve", "plan")
    graph.add_conditional_edges(
        "plan",
        should_call_tool,
        {
            "tool": "tool_router",
            "answer": "answer",
        },
    )
    graph.add_edge("tool_router", "tool_exec")
    graph.add_edge("tool_exec", "answer")
    graph.add_edge("answer", "summary")
    graph.add_edge("summary", END)

    return graph.compile()
```

---

## 14. Tool Calling 参数自修复机制

这个模块是项目亮点，建议单机版就做。

### 14.1 问题背景

LLM 选择工具时，常见失败点：

- 参数字段名错误
- 字段类型错误
- 缺少必填参数
- 字段语义不完整

### 14.2 自修复闭环

```mermaid
flowchart LR
    A["LLM 生成 Tool Input"] --> B["Pydantic 校验"]
    B -->|成功| C["执行工具"]
    B -->|失败| D["构造结构化错误"]
    D --> E["反馈给 LLM 修正"]
    E --> A
```

### 14.3 核心代码示例

```python
from pydantic import BaseModel, ValidationError


class RestartServiceInput(BaseModel):
    service_name: str
    namespace: str = "default"


def validate_tool_input(raw_args: dict):
    try:
        return True, RestartServiceInput(**raw_args).model_dump(), None
    except ValidationError as exc:
        return False, None, {
            "error_type": "validation_error",
            "details": exc.errors(),
        }
```

---

## 15. 会话记忆设计

### 15.1 当前实现中保存什么

| Key | 作用 |
|---|---|
| `SessionService.messages[session_id]` | 最近几轮对话 |
| `SessionService.summaries[session_id]` | 当前进程内历史摘要 |
| `chat_sessions.summary` | SQLite 中可恢复的摘要 |

### 15.2 策略

- 保留最近 6 到 10 轮原始消息
- 更早消息压缩成摘要
- 摘要内容包含：用户目标、已完成步骤、关键结论、未解决问题

### 15.3 当前核心代码示例

```python
class SessionService:
    def __init__(self, recent_limit: int = 8):
        self.recent_limit = recent_limit
        self._messages = {}
        self._summaries = {}

    def append_message(self, session_id: str, role: str, content: str):
        self._messages.setdefault(session_id, []).append({"role": role, "content": content})
        self._messages[session_id] = self._messages[session_id][-self.recent_limit :]

    def get_recent_messages(self, session_id: str):
        return list(self._messages.get(session_id, []))
```

### 15.4 后续扩展方向

- 若后续需要跨进程共享会话状态，可将 `SessionService` 替换为 Redis adapter。
- 当前实现已经把接口收敛在 `app/services/session_service.py`，迁移成本较低。

---

## 16. SQLite 建议存储内容

| 表名 | 用途 |
|---|---|
| `documents` | 文档信息 |
| `document_chunks` | chunk 元数据 |
| `chat_sessions` | 会话 |
| `chat_messages` | 历史消息 |
| `tool_logs` | 工具调用日志 |

### 建表示例

```sql
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    source TEXT,
    path TEXT,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS tool_logs (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    tool_name TEXT,
    input_json TEXT,
    output_json TEXT,
    status TEXT,
    created_at TEXT
);
```

---

## 17. PyQt6 演示界面设计

### 17.1 页面结构

```mermaid
flowchart LR
    A["主窗口"] --> B["左侧: 会话列表"]
    A --> C["中间: 对话区"]
    A --> D["右侧: 来源引用/工具日志"]
    A --> E["顶部: 知识库/模型/状态"]
    A --> F["底部: 输入框/发送按钮"]
```

### 17.2 MVP 页面功能

| 区域 | 功能 |
|---|---|
| 左侧 | 展示会话历史 |
| 中间 | 展示问答消息 |
| 右侧 | 展示命中文档和工具执行日志 |
| 底部 | 输入问题并发送 |

---

## 18. 建议先实现的 4 个演示场景

| 场景 | 演示内容 |
|---|---|
| 知识问答 | 输入 Redis 故障问题，返回准确答案和文档来源 |
| 故障分析 | 输入报错日志，Agent 结合文档给出诊断建议 |
| 工具调用 | 让 Agent 调用模拟工具查询服务状态 |
| 长对话压缩 | 多轮对话后仍保持上下文连贯，并显示 token 优化思路 |

---

## 19. 开发顺序建议

### 第一阶段：搭骨架

1. 初始化目录结构
2. 配置 `settings.py`
3. 跑通 Redis / SQLite / Milvus 连接
4. 实现文档 ingest 脚本

### 第二阶段：完成 RAG

1. Markdown 解析
2. chunk 切分
3. embedding 生成
4. 向量检索
5. reranker 精排
6. context builder

### 第三阶段：完成 Agent

1. 定义 `AgentState`
2. 实现 intent / retrieve / plan / answer 节点
3. 增加本地工具模拟器
4. 增加参数校验和自修复

### 第四阶段：完成 UI

1. 聊天主界面
2. 引用卡片
3. 工具日志面板
4. 会话列表

### 第五阶段：增强演示效果

1. 会话记忆服务
2. 摘要压缩
3. 日志统计面板
4. Demo 脚本

---

## 20. 最容易踩坑的问题与预防

### 20.1 检索效果差

原因：

- 切块太粗
- 标题层级丢失
- 召回结果噪音大

预防：

- 强制保留 `section_path`
- chunk 长度保持稳定
- 加 reranker
- 返回答案时必须附来源

### 20.2 Agent 工具调用不稳定

原因：

- Prompt 太自由
- 参数 schema 不清晰
- 工具输出结构不统一

预防：

- 给每个工具明确输入模型
- 统一 `ToolResult`
- 参数校验失败时返回结构化错误

### 20.3 多轮对话成本失控

原因：

- 历史消息无限堆积
- 每轮都塞满全部上下文

预防：

- recent messages + summary 双层记忆
- 控制 context chunk 数量
- 只保留最近 10 轮原始消息

### 20.4 PyQt6 界面卡顿

原因：

- 网络请求阻塞主线程
- 工具执行与 UI 绘制串行

预防：

- 后台线程执行 LLM / 检索 / 工具调用
- 使用 signal/slot 更新界面

### 20.5 演示失败

原因：

- 外部依赖过多
- 环境切换复杂
- 文档和模型没准备好

预防：

- 先准备固定 demo 数据集
- 先用本地模拟工具
- 写一个 `scripts/run_demo.py`

---

## 21. 演示时推荐的话术

可以按下面这条线介绍：

1. 这是一个面向企业研发和运维知识场景的智能自动化平台
2. 核心能力是用 RAG 提升技术文档问答准确率
3. 用自定义多节点 Agent 编排实现知识检索到运维工具调用闭环
4. 用 SessionService + SQLite Summary 做多轮会话状态管理，并通过摘要压缩降低上下文成本
5. 当前版本是单机可演示 MVP，但架构已预留企业级扩展空间

---

## 22. 第一版必须完成的文件

| 文件 | 作用 |
|---|---|
| `app/config/settings.py` | 统一配置 |
| `app/rag/chunker.py` | 文档切块 |
| `app/rag/retriever.py` | 检索逻辑 |
| `app/agent/graph.py` | Agent 编排 |
| `app/tools/ops_tools.py` | 本地工具模拟 |
| `app/services/session_service.py` | 会话记忆管理 |
| `app/ui/main_window.py` | PyQt6 主界面 |
| `scripts/ingest_docs.py` | 文档入库脚本 |

---

## 23. MVP 验收标准

| 项目 | 验收标准 |
|---|---|
| 文档入库 | 能成功读取并切分本地 Markdown 文档 |
| 检索效果 | 关键问题能命中正确文档片段 |
| Agent 编排 | 能根据问题判断是否调用工具 |
| Tool Calling | 模拟工具能正常执行并返回结构化结果 |
| 会话记忆 | 多轮对话能保留上下文 |
| UI 展示 | 能看到回答、来源、工具日志 |
| 可演示性 | 能完成至少 3 个稳定场景演示 |

---

## 24. 后续升级方向

MVP 跑通后，再逐步升级：

1. SQLite 升级 PostgreSQL
2. 本地模拟工具升级企业内部 API
3. 单一知识库升级多知识库隔离
4. 简单记忆升级结构化长期记忆
5. 本地桌面端升级 Web 管理台

---

## 25. 一句话总结

这个单机 MVP 的核心不是“做一个聊天窗口”，而是验证一条完整的企业知识自动化链路：

**文档解析 -> 检索增强 -> Agent 编排推理 -> 工具调用 -> 会话记忆 -> 桌面端可视化展示**

只要这条链路打通，这个项目就已经具备了很强的演示价值、简历价值和后续扩展价值。
