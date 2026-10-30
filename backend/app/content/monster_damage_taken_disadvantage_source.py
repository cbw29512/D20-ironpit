from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.domain.damage_taken_rules import DamageTakenDisadvantageRule
from app.domain.damage_types import DamageType
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_RULE = re.compile(
    r"(?P<name>[A-Z][A-Za-z0-9’' -]*?)\.\s+If the [^.]+ takes "
    r"(?P<dtype>Acid|Cold|Fire|Force|Lightning|Necrotic|Poison|Psychic|Radiant|Thunder) damage, "
    r"it has Disadvantage on attack rolls and ability checks until the end of its next turn\.",
    re.IGNORECASE,
)


def parse_damage_taken_disadvantage_rules(
    source_traits: object,
) -> list[DamageTakenDisadvantageRule]:
    try:
        return [
            DamageTakenDisadvantageRule(
                id=re.sub(r"[^a-z0-9]+", "-", match.group("name").lower()).strip("-"),
                name=match.group("name").strip(),
                damage_type=DamageType(match.group("dtype").lower()),
            )
            for match in _RULE.finditer(str(source_traits or ""))
        ]
    except (TypeError, ValueError):
        logger.exception("Invalid damage-taken disadvantage source trait.")
        raise
    except Exception as exc:
        logger.exception("Failed to parse damage-taken disadvantage source trait.")
        raise RuntimeError("Damage-taken disadvantage source could not be parsed.") from exc


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    try:
        return {str(row["name"]): row for row in load_monster_rows()}
    except Exception:
        logger.exception("Failed to index damage-taken disadvantage source rows.")
        raise


def complete_monster_damage_taken_disadvantage(
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
            completed.append(template.model_copy(update={
                "damage_taken_disadvantage_rules":
                    parse_damage_taken_disadvantage_rules(row.get("traits", "")),
            }))
        return completed
    except Exception as exc:
        logger.exception("Failed monster damage-taken disadvantage completion.")
        raise RuntimeError("Damage-taken disadvantage completion failed.") from exc


def damage_taken_disadvantage_trait_issues(
    template: CombatantTemplate,
    row: dict[str, object],
) -> tuple[list[str], set[str]]:
    try:
        expected = parse_damage_taken_disadvantage_rules(row.get("traits", ""))
        if template.damage_taken_disadvantage_rules != expected:
            return ["damage-taken-disadvantage-source-data-mismatch"], set()
        return [], {rule.name for rule in expected}
    except Exception as exc:
        logger.exception("Failed damage-taken disadvantage audit for %s.", template.id)
        raise RuntimeError("Damage-taken disadvantage audit failed.") from exc
