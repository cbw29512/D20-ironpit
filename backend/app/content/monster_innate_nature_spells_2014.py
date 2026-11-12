"""Source-proven 2014 innate nature spell dispositions for the standard Pit.

Schema is the unchanged printed spell/usage source, not monster-name dispatch.
Barkskin reuses the generic timed self-buff/Concentration/AC-minimum engine;
Goodberry is recorded but not selected by damage-oriented arena AI.
"""
from __future__ import annotations

import logging

from app.content.monster_innate_source_2014 import innate_spells_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.spell_modifiers import SpellModifierEffect
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)

_NATURE_SPELLS = {
    "druidcraft": ("druidcraft", "at_will", None),
    "entangle": ("entangle", "per_day", 3),
    "goodberry": ("goodberry", "per_day", 3),
    "barkskin": ("barkskin", "per_day", 1),
    "pass-without-trace": ("pass without trace", "per_day", 1),
    "shillelagh": ("shillelagh", "per_day", 1),
}


def source_proves_innate_nature_2014(monster: SourceMonster2014) -> bool:
    """Validate whole printed package; an altered ability/spell fails closed."""
    try:
        source = monster.innate_spellcasting
        if not isinstance(source, dict) or source.get("source_complete") is not True:
            return False
        if source.get("ability") != "charisma" or source.get("save_dc") != 14:
            return False
        spells = innate_spells_2014(monster)
        if len(spells) != len(_NATURE_SPELLS):
            return False
        for key, (name, usage, count) in _NATURE_SPELLS.items():
            candidates = [item for item in spells if item.get("id") == key]
            if len(candidates) != 1:
                return False
            item = candidates[0]
            if (item.get("name"), item.get("usage"), item.get("uses_per_day")) != (
                name, usage, count,
            ) or item.get("shared_pool") is not False or item.get("qualifier") is not None:
                return False
        sections = source_sections_2014(monster.source_traits, include_continuations=True)
        text = sections.get("Innate Spellcasting", "")
        return all(phrase in text for phrase in (
            "Charisma (spell save DC 14)",
            "At will: druidcraft",
            "3/day each: entangle, goodberry",
            "1/day each: barkskin, pass without trace, shillelagh",
        ))
    except Exception:
        logger.exception("Failed to prove 2014 printed innate nature spell package.")
        raise


def innate_nature_barkskin_2014(monster: SourceMonster2014) -> TimedSelfBuffAction | None:
    """A legal self-target of Touch Barkskin; self-preparation is generic."""
    try:
        if not source_proves_innate_nature_2014(monster):
            return None
        # This exact source declares AC 11, or 16 only WITH Barkskin.
        if monster.armor_class != 11 or monster.armor_class_text != "11 (16 With Barkskin)":
            raise ValueError("Printed conditional Barkskin armor class changed.")
        return TimedSelfBuffAction(
            id="barkskin", name="Barkskin", action_cost="action",
            resource_id="barkskin", resource_cost=1,
            duration_rounds=600, expiry_timing="source_turn_start",
            concentration=True, magical_effect=True, priority=85,
            modifier_effects=[
                SpellModifierEffect(kind="armor-class-minimum", minimum_value=16)
            ],
            animation="barkskin",
        )
    except Exception:
        logger.exception("Failed to bind innate 2014 Barkskin through generic timed buff.")
        raise


def source_proven_goodberry_ai_exclusion_2014(
    monster: SourceMonster2014,
) -> frozenset[str]:
    """Casting berries creates objects; arena AI does not prepare/consume them."""
    try:
        return (
            frozenset({"goodberry"})
            if source_proves_innate_nature_2014(monster) else frozenset()
        )
    except Exception:
        logger.exception("Failed to classify printed 2014 Goodberry AI exclusion.")
        raise
