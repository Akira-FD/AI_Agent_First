from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    success: bool
    code: str
    message: str
    data: Any = None
    retryable: bool = False
    error_code: str = ""
    diagnostics: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.error_code:
            self.error_code = self.code
        if self.diagnostics is None:
            self.diagnostics = {}
