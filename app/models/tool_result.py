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
