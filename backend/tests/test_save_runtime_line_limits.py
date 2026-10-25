from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_ROOT = Path(__file__).resolve().parents[2]
_SAVE_MODULES = (
    "backend/app/combat/saving_throws.py",
    "backend/app/combat/saving_throw_legality.py",
    "backend/app/combat/saving_throw_attempt.py",
    "backend/app/combat/saving_throw_damage.py",
    "backend/app/combat/saving_throw_effects.py",
    "backend/app/combat/saving_throw_event.py",
    "frontend/browser-saves.js",
    "frontend/browser-failed-save-timed-effects.js",
    "frontend/browser-save-immunity.js",
    "frontend/browser-save-action-support.js",
    "frontend/browser-save-action-attempt.js",
    "frontend/browser-save-damage.js",
    "frontend/browser-save-damage-legacy.js",
    "frontend/browser-save-damage-apply.js",
    "frontend/browser-save-action-effects.js",
    "frontend/browser-save-event.js",
)


def test_save_runtime_modules_stay_within_line_limit() -> None:
    try:
        oversized = {}
        for relative in _SAVE_MODULES:
            path = _ROOT / relative
            line_count = len(path.read_text(encoding="utf-8").splitlines())
            if line_count > 150:
                oversized[relative] = line_count
        assert oversized == {}, (
            "Save runtime modules must be split at 150 lines: "
            f"{oversized}"
        )
    except Exception:
        logger.exception("Save runtime line-limit regression check failed.")
        raise
