from __future__ import annotations

import re

from app.content.monster_catalog_2014_models import CatalogMonster2014
from app.domain.auras import StartTurnAura
from app.domain.reactions import ProjectileCatchReaction, SpellReflectionReaction


def projectile_catch_reaction_2014(source: CatalogMonster2014) -> ProjectileCatchReaction | None:
    if "Rock Catching" not in source.reaction_names:
        return None
    text = source.source_reactions or ""
    match = re.search(r"Rock Catching.*?DC\s+(\d+)\s+Dexterity saving throw", text, re.I | re.S)
    if not match:
        return None
    return ProjectileCatchReaction(save_dc=int(match.group(1)))


def spell_reflection_reaction_2014(source: CatalogMonster2014) -> SpellReflectionReaction | None:
    if "Spell Reflection" not in source.reaction_names:
        return None
    text = source.source_reactions or ""
    match = re.search(r"Spell Reflection.*?within\s+(\d+)\s+feet", text, re.I | re.S)
    if not match:
        return None
    return SpellReflectionReaction(range_ft=int(match.group(1)))


def reaction_start_turn_auras_2014(source: CatalogMonster2014) -> list[StartTurnAura]:
    if "Unnerving Mask" not in source.reaction_names:
        return []
    text = source.source_reactions or ""
    match = re.search(r"Unnerving Mask.*?starts its turn within\s+(\d+)\s+feet.*?DC\s+(\d+)\s+Wisdom saving throw", text, re.I | re.S)
    if not match:
        return []
    return [StartTurnAura(
        id="unnerving-mask", name="Unnerving Mask", range_ft=int(match.group(1)),
        save_ability="wisdom", save_dc=int(match.group(2)), failure_condition_id="frightened",
        failure_expiry_timing="target_turn_end", failure_duration_rounds=1, reaction_cost=True,
    )]


def supported_reaction_names_2014(source: CatalogMonster2014) -> set[str]:
    supported: set[str] = set()
    if source.parry_ac_bonus is not None: supported.add("Parry")
    if projectile_catch_reaction_2014(source) is not None: supported.add("Rock Catching")
    if reaction_start_turn_auras_2014(source): supported.add("Unnerving Mask")
    return supported
