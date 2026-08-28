from __future__ import annotations

import json
import logging
from pathlib import Path

from app.content.rules import build_rules_coverage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
COVERAGE_PATH = Path("frontend/rules-coverage.json")


def main() -> None:
    try:
        expected = build_rules_coverage().model_dump(mode="json")
        actual = json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))
        if actual != expected:
            raise RuntimeError(
                "frontend/rules-coverage.json does not match the FastAPI rules contract."
            )
        logger.info("Rules coverage static/API contracts match.")
    except Exception:
        logger.exception("Rules coverage synchronization check failed.")
        raise


if __name__ == "__main__":
    main()
