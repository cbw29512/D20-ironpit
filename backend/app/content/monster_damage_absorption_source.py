from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.domain.models import CombatantTemplate
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)
_ABSORPTION = re.compile(
    r"(?P<name>[A-Z][A-Za-z]+ Absorption)\.\s+Whenever the [^.]+ is subjected to "
    r"(?P<dtype>Acid|Cold|Fire|Force|Lightning|Necrotic|Poison|Psychic|Radiant|Thunder) damage, "
    r"it regains a number of Hit Points equal to the (?P=dtype) damage dealt\.",
    re.IGNORECASE,
)


def parse_damage_absorption_types(source_traits: object) -> tuple[list[DamageType], set[str]]:
    try:
        types: list[DamageType] = []
        names: set[str] = set()
        for match in _ABSORPTION.finditer(str(source_traits or "")):
            types.append(DamageType(match.group("dtype").lower()))
            names.add(match.group("name"))
        return types, names
    except Exception as exc:
        logger.exception("Failed to parse source damage absorption.")
        raise RuntimeError("Source damage absorption could not be parsed.") from exc


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    try:
        return {str(row["name"]): row for row in load_monster_rows()}
    except Exception:
        logger.exception("Failed to index monster rows for damage absorption.")
        raise


def complete_monster_damage_absorption(
    templates: list[CombatantTemplate],
) -> list[CombatantTemplate]:
    try:
        rows = _rows_by_name()
        completed: list[CombatantTemplate] = []
        for template in templates:
            if template.kind != "monster":
                completed.append(template)
                continue
            row = rows.get(template.name)
            if row is None:
                raise ValueError(f"No SRD source row for monster {template.name!r}.")
            types, _ = parse_damage_absorption_types(row.get("traits", ""))
            completed.append(template.model_copy(update={"damage_absorption_types": types}))
        return completed
    except Exception as exc:
        logger.exception("Failed to complete monster damage absorption profiles.")
        raise RuntimeError("Monster damage absorption completion failed.") from exc


def damage_absorption_trait_issues(
    template: CombatantTemplate,
    row: dict[str, object],
) -> tuple[list[str], set[str]]:
    try:
        expected_types, names = parse_damage_absorption_types(row.get("traits", ""))
        if template.damage_absorption_types != expected_types:
            return ["damage-absorption-source-data-mismatch"], set()
        return [], names
    except Exception as exc:
        logger.exception("Failed damage absorption trait audit for %s.", template.id)
        raise RuntimeError("Damage absorption trait audit failed.") from exc
