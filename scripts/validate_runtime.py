from __future__ import annotations
# ruff: noqa: E402

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config.settings import AppSettings
from app.services.llm_service import build_llm_service
from app.validation.runtime_validation import validate_runtime_capabilities


def main() -> None:
    settings = AppSettings.from_root(ROOT)
    llm_service = build_llm_service(settings)
    report = validate_runtime_capabilities(settings=settings, llm_service=llm_service)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
