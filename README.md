# AI Agent First

本仓库是基于两份架构文档生成的第一版本地 MVP 骨架代码。

当前骨架已包含：

- `Markdown -> chunk -> SQLite` 的最小文档入库链路
- 基于关键词重叠的本地检索与上下文组装
- 一版可运行的 `MVPAgent`，支持知识问答与模拟工具调用
- 内存版会话记忆服务
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
```

也兼容直接读取：

```bash
set OPENAI_API_KEY=你的APIKey
```

说明：

- 未配置 `AI_AGENT_FIRST_LLM_API_KEY` 或 `OPENAI_API_KEY` 时，系统会自动使用本地规则回答，方便离线开发和基础调试。
- 配置完成后，CLI 状态输出和桌面端页面顶部会显示当前使用的 `LLM backend`，便于确认是否真的接入远程模型。
- 如使用第三方平台，只要兼容 OpenAI Chat Completions 协议，修改 `AI_AGENT_FIRST_LLM_BASE_URL` 与模型名即可接入。

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
