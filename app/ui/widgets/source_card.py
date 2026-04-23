from __future__ import annotations


class SourceCard:
    def __init__(self, source: dict[str, object]) -> None:
        self.source = source

    def render_text(self) -> str:
        score = self.source.get("score", "")
        return (
            f"{self.source.get('section_path', self.source.get('title', '未知来源'))}\n"
            f"文件: {self.source.get('source', '')} | score: {score}\n"
            f"{self.source.get('excerpt', '')}"
        ).strip()
