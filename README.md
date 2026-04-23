# AI Agent First

本仓库是基于两份架构文档生成的第一版本地 MVP 骨架代码。

当前骨架已包含：

- `Markdown -> chunk -> SQLite` 的最小文档入库链路
- 基于关键词重叠的本地检索与上下文组装
- 一版可运行的 `MVPAgent`，支持知识问答与模拟工具调用
- recent messages + summary 的会话记忆服务，并将会话摘要持久化到 SQLite
- 已接入 OpenAI 兼容协议的大语言模型调用链路，未配置时自动回退到本地规则回答
- 桌面端 UI 的占位骨架
- `scripts/ingest_docs.py` 与 `scripts/run_demo.py` 两个脚本入口

项目当前架构、能力边界与真实测试实例见：

- `docs/PROJECT_CURRENT_ARCHITECTURE_AND_TESTING.md`

## 快速开始

```bash
python -m unittest discover -s tests -v
python scripts/ingest_docs.py
python scripts/run_demo.py
python -m app.main
python scripts/run_desktop.py
```

## 大模型接入

项目现在支持 OpenAI 兼容的 `/chat/completions` 接口。最少只需要配置 API Key，其他配置可按需覆盖：

```bash
set AI_AGENT_FIRST_LLM_API_KEY=你的APIKey
set AI_AGENT_FIRST_LLM_BASE_URL=https://api.openai.com/v1
set AI_AGENT_FIRST_LLM_MODEL=gpt-4.1-mini
set AI_AGENT_FIRST_LLM_TIMEOUT_SECONDS=30
set AI_AGENT_FIRST_LLM_RETRY_ATTEMPTS=2
set AI_AGENT_FIRST_LLM_RETRY_BACKOFF_SECONDS=0.4
```

也兼容直接读取：

```bash
set OPENAI_API_KEY=你的APIKey
```

说明：

- 未配置 `AI_AGENT_FIRST_LLM_API_KEY` 或 `OPENAI_API_KEY` 时，系统会自动使用本地规则回答，方便离线开发和基础调试。
- 配置完成后，CLI 状态输出和桌面端页面顶部会显示当前使用的 `LLM backend`，便于确认是否真的接入远程模型。
- 如使用第三方平台，只要兼容 OpenAI Chat Completions 协议，修改 `AI_AGENT_FIRST_LLM_BASE_URL` 与模型名即可接入。
- 桌面端每次回答完成后会显示回答来源：`remote` 表示真实模型返回，`fallback` 表示远程失败后使用本地规则回答。
- 中转站不稳定时可调大 `AI_AGENT_FIRST_LLM_RETRY_ATTEMPTS`，并通过 `AI_AGENT_FIRST_LLM_RETRY_BACKOFF_SECONDS` 控制退避间隔。
- 桌面端状态栏会显示 provider 诊断信息，例如 `provider=timeout`、`provider=disconnect`、`provider=http_401`、`provider=http_429`、`attempts=2`。

## Milvus 向量检索

项目现在已经支持“可选启用”的 Milvus 向量检索骨架：

```bash
set AI_AGENT_FIRST_MILVUS_ENABLED=true
set AI_AGENT_FIRST_MILVUS_URI=http://localhost:19530
set AI_AGENT_FIRST_MILVUS_COLLECTION=ai_agent_first_chunks
set AI_AGENT_FIRST_MILVUS_DIMENSION=96
```

说明：

- 未启用 Milvus，或当前环境未安装 `pymilvus`，或 Milvus 服务不可达时，系统会自动回退到当前内存检索实现。
- 启用后，`scripts/ingest_docs.py` 会在写入 SQLite 元数据的同时尝试写入 Milvus collection。
- 当前第一版接入使用本地 hash dense embedding 生成固定维度向量，后续可以继续替换为真实 embedding 模型。

## 桌面端

运行桌面端前先确保安装依赖：

```bash
python -m pip install PyQt6
```

启动 PyQt6 MVP：

```bash
python scripts/run_desktop.py
```

界面包含左侧文档列表、中间聊天区、右侧来源引用和工具日志区。默认会读取 `data/docs/` 下的 Markdown 文档并入库。

如果已经配置真实模型，桌面端顶部会显示当前后端，例如 `openai-compatible:gpt-4.1-mini`；未配置时会显示本地 fallback。
