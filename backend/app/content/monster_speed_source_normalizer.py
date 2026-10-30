from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

_RAW_SPEED = re.compile(
    r"\bSpeed\s+(?P<speed>.+?)\s+MOD\s+SAVE\b",
    re.IGNORECASE | re.DOTALL,
)


def normalize_truncated_speed_parentheticals(
    rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Repair only unbalanced structured Speed text from the complete raw stat block."""
    try:
        for row in rows:
            structured = str(row.get("speed", "")).strip()
            if structured.count("(") == structured.count(")"):
                continue
            if structured.count("(") < structured.count(")"):
                raise ValueError(
                    f"Structured Speed has an unexpected closing parenthesis for {row.get('name')!r}."
                )
            match = _RAW_SPEED.search(str(row.get("rawText", "")))
            if match is None:
                raise ValueError(
                    f"Raw Speed segment is unavailable for {row.get('name')!r}."
                )
            raw_speed = " ".join(match.group("speed").split())
            if raw_speed.count("(") != raw_speed.count(")"):
                raise ValueError(
                    f"Raw Speed segment is also unbalanced for {row.get('name')!r}: {raw_speed!r}"
                )
            stable_prefix = structured.rsplit("(", 1)[0].strip()
            if not raw_speed.startswith(stable_prefix):
                raise ValueError(
                    f"Raw Speed does not preserve the structured prefix for {row.get('name')!r}."
                )
            row["speed"] = raw_speed
        return rows
    except (TypeError, ValueError):
        logger.exception("Invalid truncated monster Speed source encountered.")
        raise
    except Exception as exc:
        logger.exception("Failed to normalize truncated monster Speed source.")
        raise RuntimeError("Truncated monster Speed normalization failed.") from exc


__all__ = ["normalize_truncated_speed_parentheticals"]
