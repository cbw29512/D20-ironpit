from __future__ import annotations

import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.domain.character_builds import AbilityScores
from app.domain.models import CombatantTemplate

_ABILITY_NAMES = {
    "Str": "strength", "Dex": "dexterity", "Con": "constitution",
    "Int": "intelligence", "Wis": "wisdom", "Cha": "charisma",
}
_SCORE_PATTERN = re.compile(r"\b(Str|Dex|Con|Int|Wis|Cha)\s+(\d+)\s+[+-]\d+\s+[+-]?\d+")
_VENDED_SCORE_TEXT_CORRECTIONS = {
    "Adult White Dragon": ("Con22 +6 +6", "Con 22 +6 +6"),
    "Young White Dragon": ("Int 6 -2 2", "Int 6 -2 -2"),
}


def _normalized_text(row: dict[str, object]) -> str:
    text = str(row.get("rawText", ""))
    correction = _VENDED_SCORE_TEXT_CORRECTIONS.get(str(row.get("name", "")))
    if correction is None:
        return text
    malformed, corrected = correction
    if malformed in text:
        return text.replace(malformed, corrected, 1)
    if corrected in text:
        return text
    raise ValueError(f"Known SRD ability-table correction no longer matches {row.get('name')!r}.")


def parse_ability_scores(row: dict[str, object]) -> AbilityScores:
    matches = _SCORE_PATTERN.findall(_normalized_text(row))
    scores = {_ABILITY_NAMES[label]: int(score) for label, score in matches}
    if set(scores) != set(_ABILITY_NAMES.values()):
        missing = sorted(set(_ABILITY_NAMES.values()) - set(scores))
        raise ValueError(f"SRD six-ability table incomplete for {row.get('name')!r}: {missing}")
    return AbilityScores(**scores)


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    return {str(row["name"]): row for row in load_monster_rows()}


def source_ability_scores(name: str) -> AbilityScores:
    row = _rows_by_name().get(name)
    if row is None:
        raise ValueError(f"No SRD 5.2.1 source row for monster {name!r}.")
    return parse_ability_scores(row)


def complete_monster_ability_scores(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    return [
        template.model_copy(update={"ability_scores": source_ability_scores(template.name)})
        if template.kind == "monster" else template
        for template in templates
    ]
