import unittest

from app.rag.chunker import MarkdownChunker
from app.rag.markdown_parser import MarkdownParser


class MarkdownParserTests(unittest.TestCase):
    def test_preserves_heading_paths_and_ignores_headings_inside_code_fences(self) -> None:
        text = """# Redis 运维

## 故障排查

先检查服务状态。

```bash
# 这不是标题
systemctl status redis
```

### 慢查询

检查 slowlog。
"""

        sections = MarkdownParser().parse(text)

        self.assertEqual([section.title for section in sections], ["故障排查", "慢查询"])
        self.assertEqual(sections[0].path, ["Redis 运维", "故障排查"])
        self.assertEqual(sections[1].path, ["Redis 运维", "故障排查", "慢查询"])
        self.assertIn("# 这不是标题", sections[0].text)


class MarkdownChunkerTests(unittest.TestCase):
    def test_splits_long_sections_with_overlap_and_keeps_section_path(self) -> None:
        text = "# Redis\n\n## 排障\n\n" + " ".join(f"step{i}" for i in range(24))
        sections = MarkdownParser().parse(text)

        chunks = MarkdownChunker(target_words=10, overlap_words=2).chunk_sections(
            doc_id="doc",
            source="redis.md",
            sections=sections,
        )

        self.assertGreaterEqual(len(chunks), 3)
        self.assertEqual(chunks[0].section_path, ["Redis", "排障"])
        self.assertTrue(chunks[0].content.endswith("step9"))
        self.assertTrue(chunks[1].content.startswith("step8 step9"))

    def test_keeps_fenced_code_block_in_one_chunk(self) -> None:
        text = """# Redis

## 重启

重启前检查状态。

```bash
systemctl stop redis
systemctl start redis
systemctl status redis
```

重启后验证连接。
"""
        sections = MarkdownParser().parse(text)

        chunks = MarkdownChunker(target_words=5, overlap_words=1).chunk_sections(
            doc_id="doc",
            source="redis.md",
            sections=sections,
        )

        code_chunks = [chunk for chunk in chunks if "systemctl stop redis" in chunk.content]
        self.assertEqual(len(code_chunks), 1)
        self.assertIn("systemctl start redis", code_chunks[0].content)
        self.assertIn("systemctl status redis", code_chunks[0].content)


if __name__ == "__main__":
    unittest.main()
