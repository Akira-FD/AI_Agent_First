from __future__ import annotations

from app.core.exceptions import ToolValidationError


def require_fields(payload: dict[str, str], required_fields: list[str]) -> dict[str, str]:
    valid, repaired, error = validate_tool_input(payload, required_fields=required_fields)
    if valid and repaired is not None:
        payload.update(repaired)
        return payload
    missing = error["missing_fields"] if error else required_fields
    if missing:
        raise ToolValidationError(f"Missing required fields: {', '.join(missing)}")
    return payload


def validate_tool_input(
    payload: dict[str, str],
    required_fields: list[str],
    aliases: dict[str, list[str]] | None = None,
) -> tuple[bool, dict[str, str] | None, dict[str, object] | None]:
    aliases = aliases or {}
    repaired = dict(payload)

    for canonical_field, alias_names in aliases.items():
        if repaired.get(canonical_field):
            continue
        for alias_name in alias_names:
            if repaired.get(alias_name):
                repaired[canonical_field] = repaired[alias_name]
                break

    missing = [field for field in required_fields if not repaired.get(field)]
    if missing:
        return (
            False,
            None,
            {
                "error_type": "validation_error",
                "missing_fields": missing,
                "received_fields": sorted(payload.keys()),
            },
        )
    return True, repaired, None
