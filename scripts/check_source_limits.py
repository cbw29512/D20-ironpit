from __future__ import annotations

import logging
from pathlib import Path

from check_shared_primitive_reuse import main as check_shared_primitive_reuse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
MAX_LINES = 150


def production_files() -> list[Path]:
    try:
        return [
            *Path("backend/app").rglob("*.py"),
            *Path("frontend").rglob("*.js"),
        ]
    except Exception as exc:
        logger.exception("Failed to discover production source files.")
        raise RuntimeError("Source discovery failed.") from exc


def main() -> None:
    try:
        offenders: list[tuple[Path, int]] = []
        for path in production_files():
            line_count = len(path.read_text(encoding="utf-8").splitlines())
            logger.info("%s: %s lines", path, line_count)
            if line_count > MAX_LINES:
                offenders.append((path, line_count))

        if offenders:
            details = ", ".join(f"{path} ({count})" for path, count in offenders)
            raise RuntimeError(f"Production files exceed {MAX_LINES} lines: {details}")
        check_shared_primitive_reuse()
    except Exception:
        logger.exception("Production source validation failed.")
        raise


if __name__ == "__main__":
    main()
