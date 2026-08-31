from __future__ import annotations

import logging
import re

from app.content.monster_catalog import load_monster_rows
from app.content.pregen_combat_profiles import build_pregen_combat_profiles
from app.domain.models import CombatantTemplate
from app.domain.unarmed import UnarmedStrikeDamage

logger = logging.getLogger(__name__)
_STR = re.compile(r"\bStr\s+(?P<score>\d+)\s+(?P<modifier>[+-]\d+)\s+[+-]\d+\b")
_PB = re.compile(r"\bPB\s+(?P<pb>[+-]\d+)\b")


def _profile(strength: int, proficiency_bonus: int) -> UnarmedStrikeDamage:
    modifier = (strength - 10) // 2
    return UnarmedStrikeDamage(
        attack_bonus=modifier + proficiency_bonus,
        damage=max(0, 1 + modifier),
    )


def monster_unarmed_profile(row: dict[str, object]) -> UnarmedStrikeDamage:
    raw = str(row.get("rawText", ""))
    strength = _STR.search(raw)
    pb = _PB.search(str(row.get("challenge", ""))) or _PB.search(raw)
    if strength is None or pb is None:
        raise ValueError(f"Could not derive Unarmed Strike profile for {row.get('name')!r}.")
    score = int(strength.group("score"))
    printed_modifier = int(strength.group("modifier"))
    if printed_modifier != (score - 10) // 2:
        raise ValueError(f"Strength modifier drift for {row.get('name')!r}.")
    return _profile(score, int(pb.group("pb")))


def _character_profiles() -> dict[str, UnarmedStrikeDamage]:
    return {
        template_id: _profile(profile.abilities.strength, 2 + (profile.level - 1) // 4)
        for template_id, profile in build_pregen_combat_profiles().items()
    }


def complete_unarmed_opportunity_profiles(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    try:
        characters = _character_profiles() if any(item.kind == "character" for item in templates) else {}
        monster_rows = (
            {str(row["name"]): row for row in load_monster_rows()}
            if any(item.kind == "monster" for item in templates)
            else {}
        )
        completed: list[CombatantTemplate] = []
        for template in templates:
            if template.kind == "character":
                profile = characters.get(template.id)
            else:
                row = monster_rows.get(template.name)
                profile = monster_unarmed_profile(row) if row is not None else None
            if profile is None:
                raise ValueError(f"No certified Unarmed Strike profile for {template.name!r}.")
            completed.append(template.model_copy(update={"unarmed_opportunity_attack": profile}))
        return completed
    except Exception as exc:
        logger.exception("Failed to derive certified Unarmed Strike Opportunity Attack profiles.")
        raise RuntimeError("Unarmed Strike Opportunity Attack profiles could not be completed.") from exc
