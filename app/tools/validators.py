from __future__ import annotations

from app.core.exceptions import ToolValidationError


def require_fields(payload: dict[str, str], required_fields: list[str]) -> dict[str, str]:
    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        raise ToolValidationError(f"Missing required fields: {', '.join(missing)}")
    return payload
