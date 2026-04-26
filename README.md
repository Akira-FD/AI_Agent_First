# AI Agent First

`AI Agent First` 是一个本地桌面端 AI Agent MVP，目标不是只做“能跑通的骨架”，而是把以下几条链路真正接起来：

- 本地知识库导入与整理
- RAG 检索、粗排、BGE 重排和上下文构造
- Agent 意图识别、工具路由、多步骤动作执行与会话摘要
- OpenAI-compatible 大模型接入与 SSE 流式输出
- 桌面端可视化交互、诊断面板与评测闭环

项目当前已经具备真实可运行能力，而不是单纯 demo：

- 真实远程 LLM 调用
- `Milvus / Milvus Lite` 向量检索
- `BGE` reranker
- 桌面端 SSE 渐进输出
- RAG 评测集与评测报告
- 受控真实工具适配器

## 本次更新

### `2026-04-27`

这次更新的功能已在代码和测试中落地，并已纳入当前 README：

- 新增 `LLM` 上下文压缩，减少送入 provider 的 prompt 体积，进一步压低首包延迟。
- 新增 `BGE` 重复问题分数缓存，相同问题重复提问或重试时可直接复用本地重排结果。
- 将 `mock tools` 升级为“受控真实工具适配器”：
  - `check_service_status` 支持真实服务状态查询
  - `search_error_logs` 支持受控日志目录真实检索
  - `restart_mock_service` 升级为默认 `dry-run` 的受控重启适配器
- 桌面端启动入口已切换为启用受控真实工具能力。
- README 与当前项目架构、能力边界、运行方式保持同步。

## 当前能力

### RAG

- 支持 `Markdown -> chunk -> SQLite` 文档入库链路
- 支持 `in-memory / milvus / milvus-lite` 检索后端切换
- 支持 `keyword-tech-weighted / bge` 两级重排
- 支持 `retrieval / coarse_rerank / bge_rerank / context_build` 分阶段耗时记录
- 支持 `BGE` 重排缓存，降低重复查询的本地耗时
- 支持来源引用、摘要化上下文和上下文长度控制

### Agent

- 支持知识问答、排查类问答、执行类请求三种主路径
- 支持多工具 action 列表执行
- 支持工具失败后的 observation / recovery / replan
- 支持 recent messages + summary 的长对话压缩与持久化
- 支持 tool logs、plan route、node trace 输出

### LLM

- 支持 OpenAI-compatible `/chat/completions`
- 支持 `gpt-5.2` 等模型名配置
- 支持 `stream=true` 的 SSE 流式输出
- 支持 timeout / disconnect / `HTTP 401` / `HTTP 429` / `HTTP 5xx` 诊断
- 支持自动重试、退避配置、fallback 回退
- 支持 provider 首包延迟、总耗时、诊断摘要展示
- 支持调用前上下文压缩，降低 prompt 体积

### Desktop UI

- 支持知识库摘要、聊天主区、来源引用、工具日志、会话摘要
- 支持实时流式输出
- 支持取消当前请求、超时提示、重试按钮
- 支持显式展示：
  - 回答来源 `remote / fallback`
  - provider 诊断
  - 首包延迟 / 总耗时
  - RAG 阶段耗时
  - retrieval / embedding / reranker backend
- 窗口默认居中启动

### 数据集与评测

- 支持从 GitHub 高信号问题构建知识文档
- 支持生成约 100 条项目相关问题测试集
- 支持评测报告导出 `JSON / Markdown`
- 支持 backend 对比维度、agent path 维度等评测汇总

### 受控真实工具

- 支持真实服务状态查询
- 支持真实日志目录检索
- 支持受控白名单服务
- 支持命令超时控制
- 支持默认 `dry-run` 的真实重启适配器
- 保留默认 mock 路径，确保测试与低风险开发体验稳定

## 推荐启动顺序

### 1. 跑测试与运行时校验

```bash
python -m unittest discover -s tests -v
python scripts/validate_runtime.py
```

### 2. 导入知识库

```bash
python scripts/ingest_docs.py
```

### 3. 启动桌面端

```bash
python scripts/run_desktop.py
```

### 4. 命令行快速查看当前运行状态

```bash
python -m app.main
```

### 5. 运行演示或评测

```bash
python scripts/run_demo.py
python scripts/run_eval.py
```

## 环境要求

- Python `>= 3.11`
- Windows 桌面环境
- 可选依赖：
  - `PyQt6`
  - `pymilvus[milvus_lite]`
  - `FlagEmbedding`
  - `transformers`

项目配置见 [pyproject.toml](pyproject.toml)。

## 大模型接入

项目支持 OpenAI-compatible 协议，既可接 OpenAI 官方，也可接兼容中转站。

### 最小配置

```bash
set AI_AGENT_FIRST_LLM_API_KEY=你的APIKey
set AI_AGENT_FIRST_LLM_BASE_URL=https://api.openai.com/v1
set AI_AGENT_FIRST_LLM_MODEL=gpt-5.2
```

也兼容：

```bash
set OPENAI_API_KEY=你的APIKey
```

### 常用调优项

```bash
set AI_AGENT_FIRST_LLM_TIMEOUT_SECONDS=30
set AI_AGENT_FIRST_LLM_RETRY_ATTEMPTS=2
set AI_AGENT_FIRST_LLM_RETRY_BACKOFF_SECONDS=0.4
set AI_AGENT_FIRST_LLM_CONTEXT_MAX_CHARS=1400
```

说明：

- 未配置 API Key 时，系统自动回退到本地规则回答。
- `AI_AGENT_FIRST_LLM_CONTEXT_MAX_CHARS` 用于控制送入 provider 的上下文大小，是本次首包优化的核心配置之一。
- 桌面端会显示 `LLM backend`，例如 `openai-compatible:gpt-5.2`。
- 桌面端状态栏与右侧面板会展示 provider 诊断，如 `provider=timeout`、`provider=disconnect`、`provider=http_429`。

## Milvus / Milvus Lite 向量检索

### 推荐单机配置

```bash
set AI_AGENT_FIRST_RETRIEVAL_BACKEND=milvus-lite
set AI_AGENT_FIRST_MILVUS_LITE_PATH=data/milvus/ai_agent_first_milvus_lite.db
set AI_AGENT_FIRST_MILVUS_COLLECTION=ai_agent_first_chunks
set AI_AGENT_FIRST_MILVUS_DIMENSION=96
set AI_AGENT_FIRST_RERANKER_BACKEND=bge
set AI_AGENT_FIRST_BGE_RERANKER_MODEL=BAAI/bge-reranker-v2-m3
```

### 可选远程 Milvus 配置

```bash
set AI_AGENT_FIRST_MILVUS_ENABLED=true
set AI_AGENT_FIRST_MILVUS_URI=http://localhost:19530
```

### BGE 相关调优

```bash
set AI_AGENT_FIRST_BGE_RERANKER_TEXT_MAX_CHARS=900
set AI_AGENT_FIRST_BGE_RERANKER_BATCH_SIZE=12
set AI_AGENT_FIRST_BGE_RERANKER_QUERY_MAX_LENGTH=48
set AI_AGENT_FIRST_BGE_RERANKER_MAX_LENGTH=160
set AI_AGENT_FIRST_BGE_RERANKER_USE_FP16=false
set AI_AGENT_FIRST_BGE_RERANKER_DEVICES=cpu
set AI_AGENT_FIRST_BGE_RERANKER_SCORE_CACHE_SIZE=256
```

说明：

- `milvus-lite` 适合当前项目的单机开发与本地验证。
- `AI_AGENT_FIRST_BGE_RERANKER_SCORE_CACHE_SIZE` 是本次新增项，可明显减少重复查询的本地 rerank 耗时。
- `data/milvus/` 和 `data/models/` 属于本地运行产物，不纳入 Git。

## 受控真实工具启用方式

桌面端和 [run_desktop.py](scripts/run_desktop.py) 现在支持受控真实工具。

### 推荐配置

```bash
set AI_AGENT_FIRST_REAL_TOOLS_ENABLED=true
set AI_AGENT_FIRST_TOOL_ALLOWED_SERVICES=redis,mysql,nginx
set AI_AGENT_FIRST_TOOL_LOG_DIRS=data/logs
set AI_AGENT_FIRST_TOOL_COMMAND_TIMEOUT_SECONDS=5
set AI_AGENT_FIRST_TOOL_RESTART_ENABLED=false
```

说明：

- `check_service_status` 会调用受控本地命令查询真实服务状态。
- `search_error_logs` 会在受控日志目录内检索真实日志文件。
- `restart_mock_service` 已升级为真实适配器，但默认只做 `dry-run` 提示。
- 只有当 `AI_AGENT_FIRST_TOOL_RESTART_ENABLED=true` 且目标服务在白名单中时，才允许执行真实重启。
- 这套真实工具能力默认只在桌面端入口启用，测试默认路径仍保持 mock 语义。

## 桌面端说明

运行桌面端前请先安装：

```bash
python -m pip install PyQt6
```

启动：

```bash
python scripts/run_desktop.py
```

当前桌面端可以观察到：

- 左侧知识库摘要
- 中间聊天区与流式回答
- 右侧来源引用
- 工具日志
- Provider 诊断
- 首包 / 总耗时
- RAG 分阶段耗时
- 当前会话摘要

## 运行时验证

运行：

```bash
python scripts/validate_runtime.py
```

会输出：

- `docs_dir_ready`
- `sqlite_dir_ready`
- `retrieval_backend`
- `embedding_backend`
- `reranker_backend`
- `llm_backend`
- `llm_remote_configured`
- `llm_sse_supported`

## 真实效果与当前瓶颈

当前项目已经做过真实链路验证，确认不是“只显示正确”，而是真的走了：

- 真实远程 `gpt-5.2`
- 真实 `Milvus`
- 真实 `BGE`
- 真实 Agent 编排
- 真实会话摘要持久化

当前主要瓶颈仍然是：

- provider 侧首包延迟
- 第一次命中某类问题时的本地 `BGE` CPU 开销
- 真实工具能力目前以观测类能力为主，生产级执行能力仍需继续扩展

## 目录结构

- `app/`
  核心源码，包含 `agent / rag / services / repositories / tools / ui`
- `data/docs/`
  本地知识库 Markdown 文档与 GitHub 采集整理后的资料
- `data/sqlite/`
  SQLite 运行时数据
- `data/milvus/`
  Milvus Lite 本地向量库运行时数据
- `docs/`
  当前架构说明、测试说明与后续执行规划文档
- `evaluation/`
  评测集、评测脚本输出与报告
- `results/`
  真实验收记录与阶段结果文件
- `scripts/`
  启动、入库、评测、验证、快捷方式安装等脚本
- `tests/`
  单元测试、集成测试与 UI 行为测试

## 相关文档

- [AI_Agent_First_MVP_Architecture.md](AI_Agent_First_MVP_Architecture.md)
- [AI_Agent_First_Development_Prompts.md](AI_Agent_First_Development_Prompts.md)
- [PROJECT_CURRENT_ARCHITECTURE_AND_TESTING.md](docs/PROJECT_CURRENT_ARCHITECTURE_AND_TESTING.md)
- [AGENT_CURRENT_ARCHITECTURE_AND_EXECUTION_PLAN.md](docs/AGENT_CURRENT_ARCHITECTURE_AND_EXECUTION_PLAN.md)
