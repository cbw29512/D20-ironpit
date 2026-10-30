from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.domain.auras import StartTurnSaveConditionAura
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_REACTION_GAZE = re.compile(
    r"(?P<name>[A-Z][A-Za-z0-9’' -]*?)\.\s+"
    r"Trigger:\s+A creature the [^.]+ can see starts its turn within (?P<radius>\d+) feet "
    r"of the [^.]+ and can see the [^.]+\.\s+"
    r"Response[-:]\s*(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) "
    r"Saving Throw:\s+DC\s+(?P<dc>\d+),\s+the triggering creature\.\s+"
    r"Failure:\s+The target has the (?P<condition>Frightened|Charmed|Poisoned) condition "
    r"until the end of its turn\.\s+"
    r"Success:\s+The target is immune to this [^’']+[’']s [^.]+ for 24 hours\.",
    re.IGNORECASE,
)


def source_reaction_start_turn_auras(source_reactions: object) -> list[StartTurnSaveConditionAura]:
    try:
        text = str(source_reactions or "").strip()
        results: list[StartTurnSaveConditionAura] = []
        for match in _REACTION_GAZE.finditer(text):
            name = match.group("name").strip()
            results.append(StartTurnSaveConditionAura(
                id=re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-"),
                name=name,
                radius_ft=int(match.group("radius")),
                save_ability=match.group("ability").lower(),
                dc=int(match.group("dc")),
                condition=match.group("condition").lower(),
                expiry_timing="target_turn_end",
                success_grants_source_immunity=True,
                requires_source_reaction=True,
            ))
        return results
    except (TypeError, ValueError):
        logger.exception("Invalid reaction start-turn aura source.")
        raise
    except Exception as exc:
        logger.exception("Failed to parse reaction start-turn aura source.")
        raise RuntimeError("Reaction start-turn aura source could not be parsed.") from exc


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    try:
        return {str(row["name"]): row for row in load_monster_rows()}
    except Exception:
        logger.exception("Failed to index reaction aura monster rows.")
        raise


def complete_monster_reaction_start_turn_auras(
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
            reaction_auras = source_reaction_start_turn_auras(row.get("reactions", ""))
            existing = [aura for aura in template.start_turn_save_condition_auras
                        if not aura.requires_source_reaction]
            completed.append(template.model_copy(update={
                "start_turn_save_condition_auras": [*existing, *reaction_auras],
            }))
        return completed
    except Exception as exc:
        logger.exception("Failed to complete reaction start-turn auras.")
        raise RuntimeError("Reaction start-turn aura completion failed.") from exc


def reaction_start_turn_aura_matches(
    template: CombatantTemplate,
    name: str,
    source_reactions: object,
) -> bool:
    try:
        expected = [
            aura for aura in source_reaction_start_turn_auras(source_reactions)
            if aura.name == name
        ]
        runtime = [
            aura for aura in template.start_turn_save_condition_auras
            if aura.name == name and aura.requires_source_reaction
        ]
        return len(expected) == 1 and runtime == expected
    except Exception as exc:
        logger.exception("Failed reaction aura audit for %s.", template.id)
        raise RuntimeError("Reaction aura audit failed.") from exc
