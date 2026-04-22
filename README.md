# AI Agent First

本仓库是基于两份架构文档生成的第一版本地 MVP 骨架代码。

当前骨架已包含：

- `Markdown -> chunk -> SQLite` 的最小文档入库链路
- 基于关键词重叠的本地检索与上下文组装
- 一版可运行的 `MVPAgent`，支持知识问答与模拟工具调用
- 内存版会话记忆服务
- 桌面端 UI 的占位骨架
- `scripts/ingest_docs.py` 与 `scripts/run_demo.py` 两个脚本入口

## 快速开始

```bash
python -m unittest discover -s tests -v
python scripts/ingest_docs.py
python scripts/run_demo.py
python -m app.main
```
