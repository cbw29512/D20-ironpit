from __future__ import annotations

from functools import lru_cache
import logging

from app.content.monster_catalog import load_monster_rows
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _types_by_name() -> dict[str, str]:
    rows = load_monster_rows()
    result = {str(row["name"]): str(row["type"]).strip() for row in rows}
    if len(result) != len(rows) or not all(result.values()):
        raise RuntimeError("Canonical SRD creature types must be complete and uniquely named.")
    return result


def source_creature_type(name: str) -> str:
    creature_type = _types_by_name().get(name)
    if creature_type is None:
        raise ValueError(f"No SRD 5.2.1 creature type for monster {name!r}.")
    return creature_type


def base_creature_type(value: str | None) -> str | None:
    if value is None:
        return None
    return value.split(" (", 1)[0].strip().casefold()


def is_creature_type(template: CombatantTemplate, expected: str) -> bool:
    return base_creature_type(template.creature_type) == expected.strip().casefold()


def creature_type_matches_source(template: CombatantTemplate) -> bool:
    return template.kind != "monster" or template.creature_type == source_creature_type(template.name)


def complete_monster_creature_types(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    try:
        completed = [
            template.model_copy(update={"creature_type": source_creature_type(template.name)})
            if template.kind == "monster" else template
            for template in templates
        ]
        if not all(creature_type_matches_source(template) for template in completed):
            raise RuntimeError("Runtime monster creature type drifted from canonical SRD source.")
        return completed
    except Exception:
        logger.exception("Failed to derive canonical monster creature types from SRD source.")
        raise
