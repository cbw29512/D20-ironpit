from __future__ import annotations

from functools import lru_cache
import logging
import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_trait_source_audit import parse_trait_names

logger = logging.getLogger(__name__)


def parse_bonus_action_names(source_bonus_actions: object) -> list[str]:
    """Preserve printed limited-use markers while reusing the proven heading parser."""
    try:
        text = str(source_bonus_actions or "").strip()
        if not text:
            return []
        base_names = parse_trait_names(text)
        names: list[str] = []
        cursor = 0
        for base_name in base_names:
            pattern = re.compile(rf"{re.escape(base_name)}(?P<marker>\s*\([^)]*\))?\.")
            match = pattern.search(text, cursor)
            if match is None:
                raise ValueError(
                    f"SRD bonus-action heading {base_name!r} could not be recovered from: {text!r}"
                )
            marker = match.group("marker") or ""
            names.append(f"{base_name}{marker}")
            cursor = match.end()
        return names
    except Exception as exc:
        logger.exception("Failed to parse source Bonus Action headings.")
        raise RuntimeError("Source Bonus Action headings could not be parsed.") from exc


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    try:
        return {str(row["name"]): row for row in load_monster_rows()}
    except Exception as exc:
        logger.exception("Failed to index SRD monster rows by name.")
        raise RuntimeError("SRD monster rows could not be indexed.") from exc


def source_bonus_action_names(name: str) -> list[str]:
    try:
        row = _rows_by_name().get(name)
        if row is None:
            raise ValueError(f"No SRD 5.2.1 source row for monster {name!r}.")
        return parse_bonus_action_names(row.get("bonusActions", ""))
    except Exception as exc:
        logger.exception("Failed to read source Bonus Actions for %s.", name)
        raise RuntimeError("Monster source Bonus Actions could not be loaded.") from exc


__all__ = ["parse_bonus_action_names", "source_bonus_action_names"]
