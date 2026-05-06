from __future__ import annotations

from html import escape


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

    def render_html(self) -> str:
        title = str(self.source.get("section_path", self.source.get("title", "未知来源")))
        source = str(self.source.get("source", ""))
        excerpt = str(self.source.get("excerpt", ""))
        score = self.source.get("score", "")
        score_text = f"{score}" if score != "" else "n/a"
        return (
            "<div class='source-card'>"
            "<div class='source-card-header'>"
            f"<div class='source-card-title'>{escape(title)}</div>"
            f"<div class='score-pill'>score {escape(score_text)}</div>"
            "</div>"
            f"<div class='source-card-meta'>文件：{escape(source)}</div>"
            f"<div class='source-card-body'>{escape(excerpt).replace(chr(10), '<br>')}</div>"
            "</div>"
        )
