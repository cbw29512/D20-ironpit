from __future__ import annotations

import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
FORBIDDEN_PATHS = (
    Path(".env.example"),
    Path("docker-compose.yml"),
    Path("backend/Dockerfile"),
    Path("backend/app/main.py"),
    Path("frontend/battle-replay.js"),
    Path("frontend/encounter-view.js"),
    Path("frontend/encounter-picker-view.js"),
    Path("frontend/encounter-picker.css"),
    Path("docs/ARENA_POLICY.md"),
    Path("docs/CURRENT_EXECUTION_FOCUS.md"),
    Path("docs/IRON_PIT_MASTER_PLAN.md"),
    Path("docs/IRON_PIT_SIMULATION_POLICY.md"),
    Path("docs/MVP.md"),
    Path("docs/ROADMAP.md"),
)


def production_files() -> list[Path]:
    try:
        return [
            *Path("backend/app").rglob("*.py"),
            *Path("frontend").rglob("*.js"),
        ]
    except Exception as exc:
        logger.exception("Failed to discover production source files.")
        raise RuntimeError("Source discovery failed.") from exc


def enforce_repository_hygiene() -> None:
    restored = [str(path) for path in FORBIDDEN_PATHS if path.exists()]
    if restored:
        raise RuntimeError(f"Removed legacy files returned: {', '.join(restored)}")

    pyproject = Path("backend/pyproject.toml").read_text(encoding="utf-8").lower()
    server_dependencies = [name for name in ("fastapi", "uvicorn") if name in pyproject]
    if server_dependencies:
        raise RuntimeError(
            "Browser-only Iron Pit must not restore HTTP server dependencies: "
            + ", ".join(server_dependencies)
        )


def main() -> None:
    """Keep architecture safeguards without enforcing arbitrary file length."""
    try:
        enforce_repository_hygiene()
        paths = production_files()
        for path in paths:
            if not path.is_file():
                raise RuntimeError(f"Expected production source is not a file: {path}")
            path.read_text(encoding="utf-8")
        logger.info("Validated %s readable production sources; no line-count restriction.", len(paths))
    except Exception:
        logger.exception("Production source/architecture validation failed.")
        raise


if __name__ == "__main__":
    main()
