from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import bootstrap_application
from app.validation.runtime_validation import validate_runtime_capabilities


def main() -> None:
    app = bootstrap_application(ROOT)
    report = validate_runtime_capabilities(settings=app.settings, llm_service=app.llm_service)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
