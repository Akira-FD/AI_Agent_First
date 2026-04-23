from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


def _read_local_env_file(root_dir: Path) -> dict[str, str]:
    env_path = root_dir / ".env"
    if not env_path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def _read_windows_persistent_env() -> dict[str, str]:
    if sys.platform != "win32":
        return {}
    try:
        import winreg
    except ImportError:
        return {}

    values: dict[str, str] = {}
    registry_targets = [
        (winreg.HKEY_CURRENT_USER, r"Environment"),
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
        ),
    ]
    for hive, subkey in registry_targets:
        try:
            with winreg.OpenKey(hive, subkey) as key:
                index = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, index)
                    except OSError:
                        break
                    if isinstance(value, str):
                        values[name] = value
                    index += 1
        except OSError:
            continue
    return values


def _get_setting(name: str, default: str, file_values: dict[str, str], persistent_values: dict[str, str]) -> str:
    if name in file_values:
        return file_values[name]
    return os.getenv(name, persistent_values.get(name, default))


@dataclass(frozen=True)
class AppSettings:
    root_dir: Path
    app_name: str
    data_dir: Path
    docs_dir: Path
    cache_dir: Path
    sqlite_path: Path
    retrieval_top_k: int
    recent_message_limit: int
    llm_api_key: str
    llm_base_url: str
    llm_model: str
    llm_timeout_seconds: int

    @classmethod
    def from_root(cls, root_dir: Path) -> "AppSettings":
        file_values = _read_local_env_file(root_dir)
        persistent_values = _read_windows_persistent_env()
        data_dir = root_dir / "data"
        docs_dir = data_dir / "docs"
        cache_dir = data_dir / "cache"
        sqlite_dir = data_dir / "sqlite"
        for path in (data_dir, docs_dir, cache_dir, sqlite_dir):
            path.mkdir(parents=True, exist_ok=True)
        return cls(
            root_dir=root_dir,
            app_name="AI Agent First",
            data_dir=data_dir,
            docs_dir=docs_dir,
            cache_dir=cache_dir,
            sqlite_path=sqlite_dir / "app.db",
            retrieval_top_k=int(_get_setting("AI_AGENT_FIRST_TOP_K", "5", file_values, persistent_values)),
            recent_message_limit=int(
                _get_setting("AI_AGENT_FIRST_RECENT_MESSAGE_LIMIT", "8", file_values, persistent_values)
            ),
            llm_api_key=_get_setting(
                "AI_AGENT_FIRST_LLM_API_KEY",
                _get_setting("OPENAI_API_KEY", "", file_values, persistent_values),
                file_values,
                persistent_values,
            ),
            llm_base_url=_get_setting(
                "AI_AGENT_FIRST_LLM_BASE_URL",
                "https://api.openai.com/v1",
                file_values,
                persistent_values,
            ),
            llm_model=_get_setting("AI_AGENT_FIRST_LLM_MODEL", "gpt-4.1-mini", file_values, persistent_values),
            llm_timeout_seconds=int(
                _get_setting("AI_AGENT_FIRST_LLM_TIMEOUT_SECONDS", "30", file_values, persistent_values)
            ),
        )
