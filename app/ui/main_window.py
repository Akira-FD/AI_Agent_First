from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DesktopAppShell:
    agent: object
    settings: object

    def render_status(self) -> str:
        return (
            f"{self.settings.app_name} MVP shell is ready.\n"
            f"Docs directory: {self.settings.docs_dir}\n"
            "UI scaffold: sessions | chat | sources | tool logs"
        )
